from odoo import models, fields

class StockWarehouseProductCost(models.Model):
    _name = 'stock.warehouse.product.cost'
    _description = 'Product Cost per Warehouse'

    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse", required=True)
    product_id = fields.Many2one('product.product', string="Product", required=True)
    cost = fields.Float(string="Cost", required=True)
