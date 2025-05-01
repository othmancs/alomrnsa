from odoo.exceptions import ValidationError
from odoo import models, api, fields

class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.constrains('quantity_done')
    def _check_quantity_done(self):
        for record in self:
            if record.picking_id.picking_type_id.code == "outgoing":
                # استخدام دالة تقريب لتجنب مشاكل الفاصلة العائمة
                quantity_done = fields.Float.round(record.quantity_done, record.product_uom.rounding)
                product_uom_qty = fields.Float.round(record.product_uom_qty, record.product_uom.rounding)
                
                if quantity_done > product_uom_qty:
                    raise ValidationError(
                        "⚠️ الكمية المنفذة (%s) لا يمكن أن تكون أكبر من الكمية المطلوبة (%s) في عملية النقل!" %
                        (quantity_done, product_uom_qty)
                    )
