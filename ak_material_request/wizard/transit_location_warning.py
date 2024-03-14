# -*- coding: utf-8 -*-
# Part of Odoo, Aktiv Software PVT. LTD.
# See LICENSE file for full copyright & licensing details.

from odoo import fields, models


class TransitLocationWarning(models.TransientModel):
    _name = "transit.location.warning"
    _description = "Material Request: Trasit Location Warning"

    name = fields.Char(string="name")

    def view_transit_location(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Locations",
            "view_mode": "tree,form",
            "res_model": "stock.location",
            "domain": [("usage", "=", "transit"), ("active", "=", False)],
            "context": {"default_usage": "transit"},
        }
