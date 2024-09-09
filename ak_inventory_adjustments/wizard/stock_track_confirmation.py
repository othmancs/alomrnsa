# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class StockTrackConfirmation(models.TransientModel):
    _inherit = "stock.track.confirmation"

    inventory_id = fields.Many2one(
        "stock.inventory", "Stock Inventory", check_company=True
    )

    def action_confirm(self):
        context = self._context
        if context.get("stock_inventory"):
            for confirmation in self:
                confirmation.inventory_id._action_done()
                if context.get("pri_ia_id_approval"):
                    confirmation.inventory_id.update(
                        {"approval_user_ids": False, "approval_status": "approved"}
                    )
                    confirmation.inventory_id.message_post(
                        body=f"<p>Approved On: {fields.datetime.now()}</p><p> Approval Note: {context.get('note',False)}</p>"
                    )

        else:
            return super().action_confirm()
