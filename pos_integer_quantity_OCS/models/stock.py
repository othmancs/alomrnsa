from odoo import models, fields, api
from odoo.exceptions import ValidationError

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    @api.constrains('product_uom', 'product_uom_qty')
    def _check_integer_quantity(self):
        for move in self:
            if move.product_id.uom_id.name == 'حبة' and float(move.product_uom_qty) % 1 != 0:
                raise ValidationError("كمية المنتج يجب أن تكون عددًا صحيحًا عندما تكون الوحدة 'حبة'")

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    
    @api.constrains('product_uom_id', 'qty_done')
    def _check_integer_quantity(self):
        for line in self:
            if line.product_id.uom_id.name == 'حبة' and float(line.qty_done) % 1 != 0:
                raise ValidationError("كمية المنتج يجب أن تكون عددًا صحيحًا عندما تكون الوحدة 'حبة'")

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    @api.constrains('product_uom', 'product_uom_qty')
    def _check_integer_quantity(self):
        for line in self:
            if line.product_id.uom_id.name == 'حبة' and float(line.product_uom_qty) % 1 != 0:
                raise ValidationError("كمية المنتج يجب أن تكون عددًا صحيحًا عندما تكون الوحدة 'حبة'")

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    @api.constrains('product_uom', 'product_qty')
    def _check_integer_quantity(self):
        for line in self:
            if line.product_id.uom_id.name == 'حبة' and float(line.product_qty) % 1 != 0:
                raise ValidationError("كمية المنتج يجب أن تكون عددًا صحيحًا عندما تكون الوحدة 'حبة'")
