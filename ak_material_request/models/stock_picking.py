# -*- coding: utf-8 -*-
# Part of Odoo, Aktiv Software PVT. LTD.
# See LICENSE file for full copyright & licensing details.

from odoo import models, fields


class StockPicking(models.Model):
    _inherit = "stock.picking"

    request_id = fields.Many2one(
        "material.request", string="Material Requisition", readonly=True, copy=False
    )

    def _create_backorder(self):
        """
        Override this method to update material request id in backorder.
        """
        backorder_recs = super(StockPicking, self)._create_backorder()
        for backorder_rec in backorder_recs:
            if backorder_rec.backorder_id.request_id:
                backorder_rec.write(
                    {"request_id": backorder_rec.backorder_id.request_id}
                )
        return backorder_recs
