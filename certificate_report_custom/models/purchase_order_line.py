from odoo import fields, models, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    sequence_number = fields.Integer(string='#', compute='_compute_sequence_number', help='Line Numbers')

    @api.depends('sequence', 'order_id')
    def _compute_sequence_number(self):
        """Function to compute line numbers"""
        for order in self.mapped('order_id'):
            sequence_number = 1
            for lines in order.order_line:
                if lines.display_type:
                    lines.sequence_number = sequence_number
                    sequence_number += 0
                else:
                    lines.sequence_number = sequence_number
                    sequence_number += 1


