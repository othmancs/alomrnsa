from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.constrains('move_lines')
    def _check_delivery_quantity(self):
        for picking in self:
            for move in picking.move_lines:
                sale_order_line = move.sale_line_id
                if sale_order_line and move.product_uom_qty > sale_order_line.product_uom_qty:
                    raise ValidationError(
                        f"لا يمكن تسليم كمية أكبر من الكمية المطلوبة ({sale_order_line.product_uom_qty}) لمنتج {move.product_id.name}."
                    )

    @api.model
    def create(self, vals):
        picking = super(StockPicking, self).create(vals)
        if picking.sale_id and picking.sale_id.state in ['sale', 'done']:
            raise UserError('لا يمكنك إضافة منتجات بعد تأكيد أمر المبيعات.')
        return picking

    def write(self, vals):
        if 'move_lines' in vals and self.sale_id and self.sale_id.state in ['sale', 'done']:
            raise UserError('لا يمكنك تعديل المنتجات بعد تأكيد أمر المبيعات.')
        return super(StockPicking, self).write(vals)
