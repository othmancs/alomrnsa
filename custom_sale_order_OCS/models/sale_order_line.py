from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    pricelist_item_id = fields.Many2one(
        'product.pricelist.item',
        string='Pricelist Item',
        compute='_compute_pricelist_item_id',
        store=True  # تخزين الحقل في قاعدة البيانات
    )

    @api.depends('product_id', 'order_id.pricelist_id')
    def _compute_pricelist_item_id(self):
        for line in self:
            # البحث عن pricelist item بناءً على المنتج وقائمة الأسعار
            line.pricelist_item_id = self.env['product.pricelist.item'].search([
                ('product_id', '=', line.product_id.id),
                ('pricelist_id', '=', line.order_id.pricelist_id.id)
            ], limit=1)
