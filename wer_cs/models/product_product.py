from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    # حقل لتخزين تكلفة المنتج حسب المستودع
    warehouse_cost_ids = fields.One2many('stock.warehouse.product.cost', 'product_id', string="Warehouse Costs")
