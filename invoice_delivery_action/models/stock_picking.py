from odoo import models, api, exceptions

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        for picking in self:
            sale_order = self.env['sale.order'].search([('name', '=', picking.origin)], limit=1)
            if sale_order:
                invoices = self.env['account.move'].search([('invoice_origin', '=', sale_order.name), ('state', '!=', 'cancel')])
                if not invoices:
                    raise exceptions.UserError("لا يمكنك تصديق أمر التسليم قبل إنشاء الفاتورة المرتبطة بأمر البيع.")
        
        # تجاوز قيود Odoo والسماح بالتصديق حتى بدون كميات محجوزة
        if self.state == 'assigned' and not any(move.quantity_done for move in self.move_lines):
            for move in self.move_lines:
                move.quantity_done = move.product_uom_qty  # ضبط الكمية المنجزة تلقائيًا
        
        return super(StockPicking, self).button_validate()
