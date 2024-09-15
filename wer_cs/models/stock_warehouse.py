from odoo import models, fields

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    # تعريف حقل تكلفة المنتج لكل مستودع
    product_cost_ids = fields.One2many('stock.warehouse.product.cost', 'warehouse_id', string="Product Costs")
