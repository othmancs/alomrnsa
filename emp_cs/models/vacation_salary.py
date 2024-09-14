from odoo import models, fields, api

class VacationSalary(models.Model):
    _name = 'vacation.salary'
    _description = 'Vacation Salary Management'

    name = fields.Char(string='Reference', required=True, readonly=True, default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    vacation_days = fields.Float(string='Vacation Days', required=True)
    salary_amount = fields.Float(string='Salary Amount', compute='_compute_salary_amount', store=True)
    date_from = fields.Date(string='From Date', required=True)
    date_to = fields.Date(string='To Date', required=True)

    @api.depends('vacation_days', 'employee_id')
    def _compute_salary_amount(self):
        for record in self:
            if record.employee_id and record.vacation_days:
                # Assuming a daily wage calculation based on monthly wage and average days
                daily_wage = record.employee_id.contract_id.wage / 30
                record.salary_amount = record.vacation_days * daily_wage

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('vacation.salary') or _('New')
        return super(VacationSalary, self).create(vals)
