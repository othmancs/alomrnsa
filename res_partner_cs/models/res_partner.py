from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_type2 = fields.Selection([
        ('cash', 'كاش'),
        ('credit', 'آجل')
    ], string='نوع العميل', default='cash')
