# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models, api, _
from dateutil.relativedelta import relativedelta


class NewJoiningEmployeeReports(models.TransientModel):
    _name = "joining.employee.reports"
    _description = "Employee Joining Reports"

    @api.model
    def default_get(self, fields_list):
        """
            Override method for get default values
        """
        res = super(NewJoiningEmployeeReports, self).default_get(fields_list)
        current_date = fields.Date.today()
        res.update({
                'start_date': current_date + relativedelta(day=1),
                'end_date': current_date + relativedelta(day=1, months=+1, days=-1),
            })
        return res

    start_date = fields.Date(string='Start Date', default=fields.Date.today(), required=True)
    end_date = fields.Date(string='End Date', default=fields.Date.today(), required=True)

    _sql_constraints = [
        ('date_check', "CHECK((start_date <= end_date))", "Please enter valid date")
    ]

    def print_reports(self):
        data = self.read()[0]
        return self.env.ref('saudi_hr.action_report_joining_employee').report_action(self, data=data)
