from odoo import models, api, fields
from odoo.exceptions import ValidationError, UserError

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.constrains('quantity_done')
    def _check_quantity_done(self):
        """منع التصديق أو الحفظ إذا كانت الكمية المنفذة أكبر من الكمية المطلوبة في أمر المبيعات."""
        for line in self:
            sale_order_line = line.move_id.sale_line_id  # احصل على سطر أمر المبيعات المرتبط
            if sale_order_line:  # تحقق من وجود سطر أمر مبيعات
                if line.quantity_done > sale_order_line.product_uom_qty:  # استخدم qty_done بدلاً من quantity_done
                    raise ValidationError(
                        f"لا يمكن تسليم كمية أكبر من الكمية المحددة ({sale_order_line.product_uom_qty}) في أمر المبيعات لمنتج {line.product_id.name}."
                    )
class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def create(self, vals):
        """منع إضافة منتجات جديدة إلى خطوط حركة المخزون بعد تأكيد أمر المبيعات."""
        picking = super(StockPicking, self).create(vals)
        if picking.sale_id and picking.sale_id.state in ['sale', 'done']:
            raise UserError('لا يمكنك إضافة منتجات جديدة بعد تأكيد أمر المبيعات.')
        return picking

    def write(self, vals):
        """منع تعديل خطوط حركة المخزون بعد تأكيد أمر المبيعات."""
        if 'move_lines' in vals and self.sale_id and self.sale_id.state in ['sale', 'done']:
            raise UserError('لا يمكنك تعديل المنتجات بعد تأكيد أمر المبيعات.')
        return super(StockPicking, self).write(vals)
