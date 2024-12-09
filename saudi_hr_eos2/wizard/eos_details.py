# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from datetime import date
from dateutil import relativedelta

from odoo import api, fields, models, _


class EOSDetails(models.TransientModel):
    _name = 'eos.details'
    _description = 'EOS Details'

    compute_at_date = fields.Selection([
        ('current_date', 'Current Date EOS'),
        ('specific_date', 'At a Specific Date')
    ], string="Compute EOS", help="Choose to analyze the current EOS or from a specific date in the past."
    , default='current_date')
    to_date = fields.Date('EOS at Date', help="Choose a date to get the EOS at that date", default=fields.Date.today())

    employee_id = fields.Many2one('hr.employee', "Employee")
    date_of_join = fields.Date(related='employee_id.date_of_join', type="date", string="Joining Date", store=True)
    department_id = fields.Many2one('hr.department', "Department", readonly=True)
    job_id = fields.Many2one('hr.job', 'Job', readonly=True)
    contract_id = fields.Many2one('hr.contract', 'Contract', readonly=True)
    duration_days = fields.Integer('No of Days', readonly=True)
    duration_months = fields.Integer('No of Months', readonly=True)
    duration_years = fields.Integer('No. of Years', readonly=True)
    total_eos = fields.Float('Total Award', readonly=True)

    def calculate_eos_reporting(self, to_date):
        """
            Calculate eos for reporting
        """
        eos_details_ids = self.env['eos.details']
        employee_ids = self.env['hr.employee'].search([])
        for employee in employee_ids:
            eos_details_values = {}
            diff = relativedelta.relativedelta(to_date, employee.date_of_join)
            duration_days = diff.days
            duration_months = diff.months
            duration_years = diff.years
            eos_details_values.update({
                'duration_days': duration_days,
                'duration_months': duration_months,
                'duration_years': duration_years
            })
            selected_month = to_date.month
            selected_year = to_date.year
            date_from = date(selected_year, selected_month, 1)
            date_to = date_from + relativedelta.relativedelta(day=to_date.day)
            contract_ids = employee._get_contracts(date_from, date_to, states=['open'])
            if contract_ids:
                # Currently your company contract wage will be calculate as last salary.
                wages = contract_ids[0].wage
                total_eos = 0.0
                if 2 <= duration_years < 5:
                    total_eos = ((wages / 2) * duration_years) + (((wages / 2) / 12) * duration_months) + ((((wages/2) / 12) / 30) * duration_days)
                elif 5 <= duration_years < 10:
                    total_eos = ((wages / 2) * duration_years) + ((wages / 12) * duration_months) + (((wages / 12) / 30) * duration_days)
                elif duration_years >= 10:
                    total_eos = ((wages / 2) * 5) + (wages * (duration_years - 5)) + ((wages / 12) * duration_months) + ((wages / 365) * duration_days)
                calc_years = round(((to_date - employee.date_of_join).days / 365.0), 2)
                payable_eos = total_eos
                # if eos.type == 'resignation':
                if 2 < calc_years < 5:
                    payable_eos = total_eos / 3
                elif 5 < calc_years < 10:
                    payable_eos = (total_eos * 2) / 3
                elif calc_years > 10:
                    payable_eos = total_eos

                eos_details_values.update({
                    'total_eos': payable_eos,
                    'employee_id': employee.id,
                    'date_of_join': employee.date_of_join,
                    'department_id': employee.department_id.id,
                    'job_id': employee.job_id.id,
                    'contract_id': contract_ids[0].id,
                    'to_date': self.to_date
                })
                eos_details_ids += self.env['eos.details'].create(eos_details_values)
        return eos_details_ids

    def open_eos_details(self):
        self.ensure_one()

        to_date = fields.Date.today()
        if self.compute_at_date == 'specific_date':
            to_date = self.to_date
        eos_details_ids = self.calculate_eos_reporting(to_date)

        tree_view_id = self.env.ref('saudi_hr_eos.view_eos_details_tree_reporting').id
        action = {
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'tree')],
            'view_mode': 'tree',
            'name': _('End of Service Reporting (EOS)'),
            'res_model': 'eos.details',
            'domain': [('id', 'in', eos_details_ids.ids)],
            'search_view_id': self.env.ref('saudi_hr_eos.view_hr_eos_details_filter').id,
        }
        return action
