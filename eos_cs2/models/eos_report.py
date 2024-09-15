from odoo import models, fields, api
from datetime import date

class Employee(models.Model):
    _inherit = 'hr.employee'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    service_years = fields.Float(string='Service Years', compute='_compute_service_years')
    basic_salary = fields.Monetary(string='Basic Salary', related='employee_id.contract_id.wage', currency_field='currency_id')
    eos_amount = fields.Monetary(string='End of Service Amount', compute='_compute_eos_amount', currency_field='currency_id')
    structure_type_id = fields.Many2one('hr.payroll.structure.type', string='Structure Type')
    schedule_pay = fields.Selection(related='structure_type_id.default_struct_id.schedule_pay', depends=())

    @api.depends('employee_id')
    def _compute_service_years(self):
        for record in self:
            start_date = record.employee_id.contract_id.date_start
            end_date = date.today()
            if start_date and isinstance(start_date, date):
                record.service_years = (end_date - start_date).days / 365.0
            else:
                record.service_years = 0.0

    @api.depends('employee_id')
    def _compute_eos_amount(self):
        for record in self:
            if record.service_years < 5:
                record.eos_amount = record.service_years * record.basic_salary * 0.5
            else:
                record.eos_amount = record.service_years * record.basic_salary
