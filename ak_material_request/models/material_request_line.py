# -*- coding: utf-8 -*-
# Part of Odoo, Aktiv Software PVT. LTD.
# See LICENSE file for full copyright & licensing details.

from odoo import api, fields, models


class MaterialRequestLine(models.Model):
    _name = "material.request.line"
    _description = "Material Request Lines"

    product_id = fields.Many2one("product.product", string="Product", required=True)
    description = fields.Char(string="Description", required=True)
    qty = fields.Float(string="Quantity", default=1, required=True)
    product_uom_category_id = fields.Many2one(
        related="product_id.uom_id.category_id", readonly=True
    )
    uom_id = fields.Many2one(
        "uom.uom",
        string="Unit of Measure",
        required=True,
        domain="[('category_id', '=', product_uom_category_id)]",
    )
    request_id = fields.Many2one("material.request")

    @api.onchange("product_id")
    def product_id_change(self):
        if self.product_id:
            self.description = self.product_id.name
            self.uom_id = self.product_id.uom_id
