# -*- coding: utf-8 -*-
import ast
import calendar
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError

MONTHS = {
    1: 'Muharram',
    2: 'Safar',
    3: 'Rabi 1',
    4: 'Rabi 2',
    5: 'Jumada 1',
    6: 'Jumada 2',
    7: 'Rajab',
    8: 'Shaban',
    9: 'Ramadan',
    10: 'Shawwal',
    11: 'Dhu al-Qadah',
    12: 'Dhu al-Hijjah',
}


def format_hijri(date):
    if not date:
        return False

    d, m, y = [x.strip() for x in date.split("/")]
    m = {MONTHS[x]: x for x in MONTHS}[m]
    return "%s-%s-%s" % (y, m, d)


class HrEmployeeIqamaDashboard(models.Model):
    _name = 'hr.employee.iqama.dashboard'
    _description = 'Employee Iqama Dashboard'

    def default_dates(self):
        today = datetime.now().date()
        end = today + relativedelta(months=3)
        return {
            'date_from': today.replace(day=1),
            'date_to': end.replace(day=calendar.monthrange(end.year, end.month)[1]),
        }

    name = fields.Char(default="IQAMA Check Expiry")
    date_from = fields.Date(default=lambda x: x.default_dates()['date_from'])
    date_to = fields.Date(default=lambda x: x.default_dates()['date_to'])

    date_from_hijri = fields.Char()
    date_to_hijri = fields.Char()

    result_without_expiry = fields.Text()
    result_to_be_expired = fields.Text()
    result_without_expiry_count = fields.Integer()
    result_to_be_expired_count = fields.Integer()
    date_mode = fields.Selection([('gregorian', 'Gregorian'), ('hijri', 'Hijri')], default='gregorian')

    def check_dates(self):
        if self.date_from > self.date_to:
            raise UserError("Date From shouldn\'t before Date To !")

    def button_search(self):
        self.update_result()

    def dashboard_data(self, date_from=None, date_to=None, date_from_hijri=None, date_to_hijri=None, date_mode='gregorian'):


        date_from = date_from or self.default_dates()['date_from']
        date_to = date_to or self.default_dates()['date_to']

        date_from_hijri = format_hijri(date_from_hijri)
        date_to_hijri = format_hijri(date_to_hijri)
        ##########################################################
        data = {}

        result_without_expiry = []
        result_to_be_expired = []

        for iqama in self.env['hr.employee.iqama'].search([]):

            if date_mode == "hijri":
                if not iqama.expiry_date_hijri:
                    result_without_expiry.append(iqama.id)
                    continue

                if date_from_hijri <= format_hijri(iqama.expiry_date_hijri) <= date_to_hijri:
                    result_to_be_expired.append(iqama.id)

            else:
                if not iqama.expiry_date:
                    result_without_expiry.append(iqama.id)
                    continue

                if date_from <= iqama.expiry_date <= date_to:
                    result_to_be_expired.append(iqama.id)

        data['result_without_expiry'] = result_without_expiry and str(result_without_expiry) or ""
        data['result_to_be_expired'] = result_to_be_expired and str(result_to_be_expired) or ""
        data['result_without_expiry_count'] = len(result_without_expiry or [])
        data['result_to_be_expired_count'] = len(result_to_be_expired or [])
        return data

    def update_result(self):
        self.ensure_one()
        self.check_dates()
        data = self.dashboard_data(date_from=self.date_from, date_to=self.date_to, date_from_hijri=self.date_from_hijri, date_to_hijri=self.date_to_hijri, date_mode=self.date_mode)
        self.update(data)

    @api.model
    def default_get(self, _fields):
        res = super(HrEmployeeIqamaDashboard, self).default_get(_fields)
        data = self.dashboard_data()
        for field, val in data.items():
            res[field] = val
        return res

    def open_iqama_list(self):
        self.ensure_one()
        self.update_result()
        mode = self._context.get('mode')
        action = {
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'hr.employee.iqama',
            'target': 'new',
        }
        if mode == "to_be_expired":
            action['name'] = "%s IQAMA are going to be expired" % self.result_to_be_expired_count
            ids = ast.literal_eval(self.result_to_be_expired or "[]")
            action['domain'] = [('id', 'in', ids)]

        elif mode == "without_expiry":
            action['name'] = "%s IQAMA hasn't expiry date." % self.result_without_expiry_count
            ids = ast.literal_eval(self.result_without_expiry or "[]")
            action['domain'] = [('id', 'in', ids)]

        else:
            raise NotImplementedError

        return action


