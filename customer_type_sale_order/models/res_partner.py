from odoo import fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_type2 = fields.Selection(
        [('cash', 'كاش'), ('credit', 'آجل')],
        string='نوع العميل',
        default='cash',
        required=True,
        store=True,
    )
