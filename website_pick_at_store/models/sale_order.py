from odoo import fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    store_address_id = fields.Many2one('res.partner')
