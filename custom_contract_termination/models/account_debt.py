from odoo import models, fields

class AccountDebt(models.Model):
    _name = 'account.debt'
    _description = 'Employee Debt'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    amount = fields.Float(string='Amount', required=True)
    state = fields.Selection([
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('pending', 'Pending')
    ], string='State', default='open', required=True)
    date = fields.Date(string='Debt Date', default=fields.Date.today)

    def pay_debt(self):
        self.state = 'paid'

    def set_pending(self):
        self.state = 'pending'
