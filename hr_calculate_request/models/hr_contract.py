from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta


class HrContract(models.Model):
    _inherit = 'hr.contract'

    end_service_date = fields.Date(string="End of Service Date")
    basic_salary = fields.Float(string="Basic Salary", compute='_compute_basic_salary', digits=(16, 2))
    indemnity_amount = fields.Float(string='EOS Amount', compute='_compute_employee_end_service')
    vacation_liquidation_amount = fields.Float(string='Vacation Liquidation Amount', compute='_compute_vacation_liquidation_amount')
    work_years = fields.Float(string='Work Years', readonly=True, compute='_compute_work_years')

    @api.depends('date_start', 'date_end')
    def _compute_work_years(self):
        for contract in self:
            if contract.date_start and contract.date_end:
                from_date = fields.Date.from_string(contract.date_start)
                end_date = fields.Date.from_string(contract.date_end)
                contract.work_years = (end_date - from_date).days / 365.25
            else:
                contract.work_years = 0


    def _compute_basic_salary(self):
        for contract in self:
            payslip_lines = self.env['hr.payslip.line'].search([
                ('employee_id', '=', contract.employee_id.id),
                ('code', '=', 'BASIC')
            ], limit=3, order='date_to desc')
            contract.basic_salary = sum(payslip_lines.mapped('amount')) / len(payslip_lines) if payslip_lines else 0

    #
    def _calculate_indemnity(self, service_years):
        first_work = 0.0
        if service_years >= 5:
            first_work = 5
            service_years = service_years - first_work
        else:
            service_years = service_years
        first_calculate = self.basic_salary * first_work * 0.5
        last_calculate = self.basic_salary * service_years
        return first_calculate + last_calculate

    def _calculate_indemnity_vacation_liquidation_amount(self, service_years):
        first_work = 0.0
        if service_years >= 5:
            first_work = 5
            service_years = service_years - first_work
        else:
            service_years = service_years
        first_calculate = (self.basic_salary / 30) * (first_work * 21)
        last_calculate = self.basic_salary * service_years
        return first_calculate + last_calculate
    # @api.depends('date_start', 'date_end')
    # def _compute_work_years(self):
    #     for contract in self:
    #         if contract.date_start and contract.date_end:
    #             from_date = fields.Date.from_string(contract.date_start)
    #             end_date = fields.Date.from_string(contract.date_end)
    #             contract.work_years = (end_date - from_date).days / 365.25
    #         else:
    #             contract.work_years = 0

    # def _compute_work_years(self):
    #     for contract in self:
    #         if contract.date_start and contract.date_end:
    #             from_date = fields.Date.from_string(contract.date_start)
    #             end_date = fields.Date.from_string(contract.date_end)
    #             contract.work_years = (end_date - from_date).days / 365.25
    #         else:
    #             contract.work_years = 0

    # work_years = fields.Float(string='Work Years', readonly=True, compute='_compute_work_years')

    def _compute_employee_end_service(self):
        for contract in self:
            if contract.date_start and contract.date_end:
                contract.indemnity_amount = contract._calculate_indemnity(contract.work_years)

    def _compute_vacation_liquidation_amount(self):
        for contract in self:
            if contract.date_start and contract.date_end:
                contract.vacation_liquidation_amount = contract._calculate_indemnity_vacation_liquidation_amount(
                    contract.work_years)
