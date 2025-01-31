from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    customer_type2 = fields.Selection([
        ('cash', 'كاش'),
        ('credit', 'آجل')
    ], string='نوع العميل', related='partner_id.customer_type2', readonly=True, store=True)
