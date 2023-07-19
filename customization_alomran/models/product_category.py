from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    stock_warehouse_id = fields.Many2one('stock.warehouse', string='Stock Warehouse')
