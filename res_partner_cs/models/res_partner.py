from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_type2 = fields.Selection([
        ('cash', 'Cash'),
        ('credit', 'Credit')
    ], string='Customer Type', default='cash')
