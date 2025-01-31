from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_type2 = fields.Selection([
        ('نقدي', 'cash'),
        ('آجل', 'credit')
    ], string='نوع العميل', default='cash')
