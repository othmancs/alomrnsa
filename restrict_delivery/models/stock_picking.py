from odoo import models, fields, api
from odoo.exceptions import ValidationError

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
