from odoo import models, fields, api

class EndOfService(models.Model):
    _name = 'end.of.service'
    _description = 'End of Service Management'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    termination_reason = fields.Selection([('resignation', 'Resignation'), 
                                            ('contract_end', 'Contract End')], string="Reason")
    termination_date = fields.Date(string="Termination Date")
    years_of_service = fields.Float(string="Years of Service", compute="_compute_years_of_service")
    gratuity_amount = fields.Float(string="Gratuity Amount", compute="_compute_gratuity")

    @api.depends('termination_date', 'employee_id.contract_id.date_start')
    def _compute_years_of_service(self):
        for record in self:
            if record.termination_date and record.employee_id.contract_id.date_start:
                delta = record.termination_date - record.employee_id.contract_id.date_start
                record.years_of_service = delta.days / 365

    @api.depends('years_of_service', 'termination_reason', 'employee_id.contract_id.wage')
    def _compute_gratuity(self):
        for record in self:
            basic_salary = record.employee_id.contract_id.wage
            years = record.years_of_service
            if record.termination_reason == 'resignation':
                if years < 2:
                    record.gratuity_amount = 0
                elif years <= 5:
                    record.gratuity_amount = (basic_salary * 0.5 * years) / 3
                elif years <= 10:
                    record.gratuity_amount = (basic_salary * 0.5 * 5) + ((basic_salary * 1 * (years - 5)) * 2/3)
                else:
                    record.gratuity_amount = (basic_salary * 0.5 * 5) + (basic_salary * 1 * (years - 5))
            elif record.termination_reason == 'contract_end':
                record.gratuity_amount = (basic_salary * 0.5 * 5) + (basic_salary * 1 * (years - 5))
