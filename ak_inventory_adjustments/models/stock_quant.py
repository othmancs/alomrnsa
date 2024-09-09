# -*- coding: utf-8 -*-

from odoo import models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def action_view_inventory(self):
        res = super().action_view_inventory()
        if res.get("name"):
            res.update({"name": "Quants"})
        return res
