# -*- coding: utf-8 -*-
from odoo import api, models


class Product(models.Model):
    _inherit = "product.product"

    @api.model
    def get_theoretical_quantity(
        self,
        product_id,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        to_uom=None,
    ):
        product_id = self.env["product.product"].browse(product_id)
        product_id.check_access_rights("read")
        product_id.check_access_rule("read")
        location_id = self.env["stock.location"].browse(location_id)
        lot_id = self.env["stock.lot"].browse(lot_id)
        package_id = self.env["stock.quant.package"].browse(package_id)
        owner_id = self.env["res.partner"].browse(owner_id)
        to_uom = self.env["uom.uom"].browse(to_uom)
        quants = self.env["stock.quant"]._gather(
            product_id,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=True,
        )
        if lot_id:
            quants = quants.filtered(lambda q: q.lot_id == lot_id)
        theoretical_quantity = sum([quant.quantity for quant in quants])
        if to_uom and product_id.uom_id != to_uom:
            theoretical_quantity = product_id.uom_id._compute_quantity(
                theoretical_quantity, to_uom
            )
        return theoretical_quantity
