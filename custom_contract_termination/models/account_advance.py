from odoo import models, fields

class AccountAdvance(models.Model):
    _name = 'account.advance'
    _description = 'Employee Advance'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    amount = fields.Float(string='Amount', required=True)
    state = fields.Selection([
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('pending', 'Pending')
    ], string='State', default='open', required=True)
    date = fields.Date(string='Advance Date', default=fields.Date.today)

    def pay_advance(self):
        self.state = 'paid'

    def set_pending(self):
        self.state = 'pending'
