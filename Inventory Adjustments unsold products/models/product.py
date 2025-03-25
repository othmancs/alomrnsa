from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # إضافة حقل لحساب التعديلات التي تم إجراؤها على المنتجات
    adjustment_count = fields.Integer(string="Inventory Adjustments Count", compute='_compute_inventory_adjustments')

    @api.depends('stock_valuation_layer_ids')
    def _compute_inventory_adjustments(self):
        for product in self:
            # استعلام لمعرفة ما إذا كان المنتج تم تعديله في جرد
            product.adjustment_count = len(product.stock_valuation_layer_ids)
