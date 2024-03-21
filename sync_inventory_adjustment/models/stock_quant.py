# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _get_inventory_move_values(self, qty, location_id, location_dest_id, out=False):
        move_vals = super(StockQuant, self)._get_inventory_move_values(qty, location_id, location_dest_id, out)
        context = dict(self.env.context) or {}
        move_vals.update({'inventory_id': context.get('inventory_id')})
        return move_vals