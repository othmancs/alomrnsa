from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta

class HrContract(models.Model):
    _inherit = 'hr.contract'

    end_service_date = fields.Date(string="End of Service Date")
    basic_salary = fields.Float(string="Basic Salary", compute='_compute_basic_salary', digits=(16, 2))
    indemnity_amount = fields.Float(string='EOS Amount', compute='_compute_employee_end_service', digits=(16, 2))
    vacation_liquidation_amount = fields.Float(string='Vacation Liquidation Amount', compute='_compute_vacation_liquidation_amount', digits=(16, 2))
    work_years = fields.Float(string='Work Years', readonly=True, compute='_compute_work_years', digits=(16, 2))

    @api.depends('date_start', 'date_end')
    def _compute_work_years(self):
        for contract in self:
            if contract.date_start and contract.date_end:
                from_date = fields.Date.from_string(contract.date_start)
                end_date = fields.Date.from_string(contract.date_end)
                contract.work_years = (end_date - from_date).days / 365.25
            else:
                contract.work_years = 0.0

    @api.depends('employee_id', 'date_start')
    def _compute_basic_salary(self):
        for contract in self:
            payslip_lines = self.env['hr.payslip.line'].search([
                ('employee_id', '=', contract.employee_id.id),
                ('code', '=', 'BASIC')
            ], limit=3, order='date_to desc')
            contract.basic_salary = sum(payslip_lines.mapped('amount')) / len(payslip_lines) if payslip_lines else 0.0

    def _calculate_indemnity(self, service_years):
        if service_years <= 0:
            return 0.0
        elif service_years < 5:
            return self.basic_salary * service_years * 0.5  # نصف شهر عن كل سنة أقل من 5 سنوات
        else:
            return (self.basic_salary * 5 * 0.5) + (self.basic_salary * (service_years - 5))  # نصف شهر عن أول 5 سنوات + شهر عن كل سنة بعد ذلك

    def _calculate_indemnity_vacation_liquidation_amount(self, service_years):
        if service_years <= 0:
            return 0.0
        elif service_years < 5:
            return (self.basic_salary / 30) * (service_years * 21)  # 21 يوم إجازة لكل سنة أقل من 5 سنوات
        else:
            return (self.basic_salary / 30) * (5 * 21) + (self.basic_salary * (service_years - 5))  # 21 يوم عن أول 5 سنوات + شهر لكل سنة بعد ذلك

    @api.depends('date_start', 'date_end')
    def _compute_employee_end_service(self):
        for contract in self:
            if contract.work_years > 0:
                contract.indemnity_amount = contract._calculate_indemnity(contract.work_years)

    @api.depends('date_start', 'date_end')
    def _compute_vacation_liquidation_amount(self):
        for contract in self:
            if contract.work_years > 0:
                contract.vacation_liquidation_amount = contract._calculate_indemnity_vacation_liquidation_amount(contract.work_years)
