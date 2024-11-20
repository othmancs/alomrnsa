from odoo import models, fields

class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    def get_missing_items(self):
        """إرجاع الأصناف غير المجرودة"""
        self.ensure_one()
        missing_items = self.env['stock.inventory.line'].search([
            ('inventory_id', '=', self.id),
            ('product_qty', '=', 0),  # لم يتم جردها
            ('theoretical_qty', '!=', 0)  # لها كمية نظرية
        ])
        return missing_items
