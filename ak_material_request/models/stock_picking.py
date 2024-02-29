# -*- coding: utf-8 -*-
# Part of Odoo, Aktiv Software PVT. LTD.
# See LICENSE file for full copyright & licensing details.

from odoo import models, fields, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    request_id = fields.Many2one(
        "material.request", string="Material Requisition", readonly=True, copy=False
    )

    # To Disable Validation
    main_picking = fields.Many2one('stock.picking')

    def button_validate(self):
        for rec in self:
            if rec.main_picking and rec.main_picking.state != 'done':
                # raise ValidationError(_('This Transfer is Waiting for another one before Validating'))
                raise ValidationError('يجب الموافقه على امر التوصيل الاساسى قبل هذا')
            return super().button_validate()

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
