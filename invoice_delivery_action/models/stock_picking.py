from odoo import models, exceptions

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        """
        تعديل وظيفة تصديق أمر التسليم (Stock Picking) للسماح بإنشاء الفاتورة قبل تصديق الكميات.
        """
        # تجاوز قيود Odoo والسماح بالتصديق حتى بدون كميات محجوزة
        if self.state == 'assigned' and not any(move.quantity_done for move in self.move_ids):
            for move in self.move_ids:
                move.quantity_done = move.product_uom_qty  # ضبط الكمية المنجزة تلقائيًا
        
        # السماح بالتصديق دون التحقق من وجود فاتورة
        return super(StockPicking, self).button_validate()
