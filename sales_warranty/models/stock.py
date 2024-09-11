# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _action_done(self):
        """
            Override method for start warranty and cancel Warranty
        """
        res = super(StockPicking, self)._action_done()
        for pick in self:
            for move_line in pick.move_line_ids.filtered(lambda l: l.state == 'done' and l.move_id):
                if move_line.move_id.sale_line_id:
                    for warranty in move_line.move_id.sale_line_id.warranty_details.filtered(lambda l: not l.serial_id and l.state == 'pending'):
                        warranty.serial_id = move_line.lot_id.id
                        break
                    for warranty in move_line.move_id.sale_line_id.warranty_details.filtered(lambda l: l.serial_id and l.sale_invoice_id and l.state == 'pending'):
                        warranty.action_running()
                    if pick.picking_type_code == 'incoming':
                        for warranty in move_line.move_id.sale_line_id.warranty_details.filtered(lambda l: move_line.product_id == l.product_id and l.serial_id == move_line.lot_id and l.state == 'running'):
                            warranty.action_cancel()
        return res
