from odoo.exceptions import ValidationError
from odoo import models, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.constrains('quantity_done')
    def _check_quantity_done(self):
        for record in self:
            if record.picking_id.picking_type_id.code == "outgoing":  # تحقق من أن العملية "خروج"
                if record.quantity_done > record.product_uom_qty:  # الكمية المنفذة لا تتجاوز الكمية المطلوبة
                    raise ValidationError("⚠️ الكمية المنفذة لا يمكن أن تكون أكبر من الكمية المطلوبة في عملية النقل!")
