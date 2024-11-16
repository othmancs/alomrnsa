from odoo import models, fields, api

class EndOfService(models.Model):
    _name = 'end.of.service'
    _description = 'End of Service Calculation (Saudi Law)'

    name = fields.Char(
        string='Reference', 
        required=True, 
        copy=False, 
        default='New', 
        readonly=True
    )
    employee_id = fields.Many2one(
        'hr.employee', 
        string='Employee', 
        required=True
    )
    contract_id = fields.Many2one(
        'hr.contract', 
        string='Contract', 
        required=True
    )
    reason_id = fields.Many2one(
        'end.of.service.reason', 
        string='Reason for Termination'
    )
    service_years = fields.Float(
        string='Service Years', 
        compute='_compute_service_years', 
        store=True
    )
    currency_id = fields.Many2one(
        'res.currency', 
        string='Currency', 
        default=lambda self: self.env.company.currency_id
    )
    basic_salary = fields.Monetary(
        string='Basic Salary', 
        related='contract_id.wage', 
        readonly=True, 
        currency_field='currency_id'
    )
    total_benefits = fields.Float(
        string='Total Benefits', 
        compute='_compute_total_benefits', 
        store=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
    ], string='Status', default='draft')

    @api.depends('contract_id')
    def _compute_service_years(self):
        for record in self:
            if record.contract_id:
                start_date = record.contract_id.date_start
                end_date = record.contract_id.date_end or fields.Date.today()
                record.service_years = (end_date - start_date).days / 365.0

    @api.depends('service_years', 'basic_salary', 'reason_id')
    def _compute_total_benefits(self):
        for record in self:
            years = record.service_years
            salary = record.basic_salary

            if years <= 5:
                base_amount = (salary / 2) * years
            else:
                base_amount = (salary / 2) * 5 + salary * (years - 5)

            # Adjusting based on resignation scenarios
            if record.reason_id and record.reason_id.code == 'resignation':
                if years < 2:
                    record.total_benefits = 0
                elif 2 <= years < 5:
                    record.total_benefits = base_amount * 1 / 3
                elif 5 <= years < 10:
                    record.total_benefits = base_amount * 2 / 3
                else:
                    record.total_benefits = base_amount
            else:
                record.total_benefits = base_amount
