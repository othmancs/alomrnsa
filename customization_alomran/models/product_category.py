from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    stock_warehouse_ids = fields.Many2many('stock.warehouse', string='Stock Warehouses')
