# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, models


class StockWarnInsufficientQtyRepair(models.TransientModel):
    _inherit = "stock.warn.insufficient.qty.repair"

    def action_done(self):
        """
        Override method for the check procurement rules
        """
        context = dict(self.env.context)
        if context.get("active_id") and context.get("active_model") == "repair.order":
            repair_id = self.env["repair.order"].browse(context["active_id"])
            repair_id.operations._action_launch_stock_rule()
        return super(StockWarnInsufficientQtyRepair, self).action_done()
