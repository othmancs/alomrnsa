
from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    pricelist_item_id = fields.Many2one('product.pricelist.item', store=True)  # جعل الحقل مخزنًا
