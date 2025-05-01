from odoo.exceptions import ValidationError
from odoo import models, api, fields, _

class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.constrains('quantity_done')
    def _check_quantity_done(self):
        for record in self:
            if not record.picking_id or not record.picking_id.picking_type_id:
                continue
                
            if record.picking_id.picking_type_id.code == "outgoing":
                # التحقق من وجود وحدات القياس وتطابقها
                if not record.product_uom:
                    continue
                    
                # التقريب حسب دقة الوحدة المستخدمة
                precision = record.product_uom.rounding
                qty_done = fields.Float.round(record.quantity_done, precision)
                qty_expected = fields.Float.round(record.product_uom_qty, precision)
                
                # إضافة هامش صغير للتعامل مع أخطاء الفاصلة العائمة
                float_compare = fields.Float.compare(qty_done, qty_expected, precision_rounding=precision)
                
                if float_compare == 1:  # 1 يعني أن الكمية المنفذة أكبر
                    raise ValidationError(_(
                        "⚠️ الكمية المنفذة (%s %s) لا يمكن أن تكون أكبر من الكمية المطلوبة (%s %s) في عملية النقل!") % (
                        qty_done, record.product_uom.name,
                        qty_expected, record.product_uom.name
                    ))
