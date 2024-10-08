from odoo import models, api, fields
from odoo.exceptions import ValidationError, UserError

class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.constrains('quantity_done')
    def _check_quantity_done(self):
        """منع التصديق أو الحفظ إذا كانت الكمية المنفذة أكبر من الكمية المطلوبة في الحركة."""
        for move in self:
            if move.quantity_done > move.product_uom_qty:
                raise ValidationError(
                    f"لا يمكن التصديق لأن الكمية المنفذة ({move.quantity_done}) أكبر من الكمية المحددة ({move.product_uom_qty}) للمنتج {move.product_id.name}."
                )

    def button_validate(self):
        """التأكد من عدم تجاوز الكمية قبل التصديق."""
        self._check_quantity_done()  # تأكد من التحقق قبل التصديق
        return super(StockMove, self).button_validate()  # اتصل بإجراء التصديق الأساسي

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
