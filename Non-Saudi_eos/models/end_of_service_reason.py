from odoo import models, fields

class EndOfServiceReason(models.Model):
    _name = 'end.of.service.reason'
    _description = 'Reason for End of Service'

    name = fields.Char(string='Reason', required=True)
    code = fields.Selection([
        ('resignation', 'Resignation'),
        ('termination', 'Termination'),
        ('unjust', 'Unjust Termination'),
    ], string='Code', required=True)
