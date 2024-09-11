# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class NewJoiningEmployee(models.AbstractModel):
    _name = 'report.saudi_hr.report_emp_birthday_list'
    _description = "New Joining Employee"

    @api.model
    def _get_report_values(self, doc_ids, data=None):
        if not data.get('id') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        employees = self.env['hr.employee'].search([('birthday', '!=', False)]).filtered(lambda l: l.birthday.month >= int(data['start_month']) and
            l.birthday.month <= int(data['end_month']) and l.birthday.day >= int(data['start_day']) and l.birthday.day <= int(data['end_day']))
        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data,
            'docs': docs,
            'employees': employees,
        }