from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_type = fields.Selection([
        ('cash', 'Cash'),
        ('credit', 'Credit')
    ], string='Customer Type', default='cash')
