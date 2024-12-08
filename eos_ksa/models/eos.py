from odoo import models, fields, api

class EmployeeEOS(models.Model):
    _name = 'employee.eos'
    _description = 'End of Service'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    total_years = fields.Float(string='Total Years of Service', compute='_compute_total_years', store=True)
    eos_amount = fields.Float(string='EOS Amount', compute='_compute_eos_amount', store=True)

    @api.depends('start_date', 'end_date')
    def _compute_total_years(self):
        for record in self:
            if record.start_date and record.end_date:
                delta = record.end_date - record.start_date
                record.total_years = delta.days / 365.0

    @api.depends('total_years')
    def _compute_eos_amount(self):
        for record in self:
            if record.total_years <= 5:
                record.eos_amount = record.total_years * 15  # Placeholder logic
            else:
                record.eos_amount = (5 * 15) + ((record.total_years - 5) * 30)
