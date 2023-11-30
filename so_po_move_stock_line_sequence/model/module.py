
from odoo import api, fields, models, _


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    sequence2 = fields.Integer(string='#', compute='_compute_sequence', help='Line Numbers')

    @api.depends('sequence2', 'order_id')
    def _compute_sequence(self):
        for order in self.mapped('order_id'):
            sequence = 1
            for lines in order.order_line:
                if lines.display_type:
                    lines.sequence2 = sequence
                    sequence += 0
                else:
                    lines.sequence2 = sequence
                    sequence += 1

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    sequence2 = fields.Integer(string='#', compute='_compute_sequence', help='Line Numbers')

    @api.depends('sequence2', 'order_id')
    def _compute_sequence(self):
        for order in self.mapped('order_id'):
            sequence = 1
            for lines in order.order_line:
                if lines.display_type:
                    lines.sequence2 = sequence
                    sequence += 0
                else:
                    lines.sequence2 = sequence
                    sequence += 1

class StockMove(models.Model):
    _inherit = 'stock.move'

    sequence2 = fields.Integer(string='#', compute='_compute_sequence', help='Line Numbers')

    @api.onchange('product_id')
    def _compute_sequence(self):
        sequence = 1
        for line in self:
            if not line.product_id:
                continue
            else:
                line.sequence2 = sequence
                sequence += 1

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    sequence2 = fields.Integer(string='#', compute='_compute_sequence2', help='Line Numbers',store=True)


    @api.depends('display_type')
    def _compute_sequence2(self):
        sequence = 1
        for line in self:
            if line.display_type == 'product':
                line.sequence2 = sequence
                sequence += 1
            else:
                line.sequence2 = False


