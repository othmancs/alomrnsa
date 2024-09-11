# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class Repair(models.Model):
    _inherit = "repair.order"

    @api.model
    def _default_warehouse_id(self):
        return self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.company.id)], limit=1
        )

    def calculate_purchases(self):
        """
        Compute purchase record numbers
        """
        for rec in self:
            rec.purchase_count = self.env["purchase.order"].search_count(
                [("origin", "=", rec.name)]
            )

    purchase_count = fields.Integer(string="# Purchase", compute="calculate_purchases")
    warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Warehouse",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=_default_warehouse_id,
    )

    @api.onchange("warehouse_id")
    def _onchange_warehouse_id(self):
        if self.warehouse_id and self.warehouse_id.company_id:
            self.company_id = self.warehouse_id.company_id.id

    def action_validate(self):
        """
        Check procurement rules and create purchase order
        """
        res = super(Repair, self).action_validate()

        self.ensure_one()
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for repair in self:
            available_qty = self.env["stock.quant"]._get_available_quantity(
                repair.product_id, repair.location_id, repair.lot_id, strict=True
            )
            if (
                float_compare(
                    available_qty, repair.product_qty, precision_digits=precision
                )
                >= 0
            ):
                repair.operations._action_launch_stock_rule()
        return res

    def action_repair_start(self):
        """
        Checks if all parts quantities are available in stock before starting a repair and raises an error if not.
        """
        for repair in self:
            for line in repair.operations:
                if (
                    line.product_id.type == "product"
                    and line.product_uom_qty > line.available_qty
                ):
                    raise UserError(
                        _(
                            "Before start repair need to be all parts quantity are available in stock!"
                        )
                    )
        return super(Repair, self).action_repair_start()

    def action_view_purchase(self):
        """
        Show purchase orders
        """
        action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_rfq")
        purchase_ids = self.env["purchase.order"].search([("origin", "=", self.name)])
        if len(purchase_ids) > 1:
            action["domain"] = [("id", "in", purchase_ids.ids)]
        elif purchase_ids:
            action["views"] = [
                (self.env.ref("purchase.purchase_order_form").id, "form")
            ]
            action["res_id"] = purchase_ids[0].id
        return action


class RepairLine(models.Model):
    _inherit = "repair.line"

    def calculate_available_qty(self):
        """
        Calculate available quantaties
        """
        for rec in self:
            rec.available_qty = 0
            if rec.product_id.type == "product":
                available_qty = (
                    self.env["stock.quant"]
                    .search(
                        [
                            ("location_id", "child_of", rec.location_id.id),
                            ("location_id.usage", "=", "internal"),
                            ("product_id", "=", rec.product_id.id),
                        ]
                    )
                    .mapped("quantity")
                )
                rec.available_qty = sum(available_qty) if available_qty else 0

    available_qty = fields.Float(
        string="OnHand Quantity", compute="calculate_available_qty"
    )

    @api.onchange("repair_id", "product_id", "product_uom_qty")
    def onchange_product_id(self):
        super(RepairLine, self).onchange_product_id()
        if self.product_id.type == "product" and self.type == "add":
            precision = self.env["decimal.precision"].precision_get(
                "Product Unit of Measure"
            )
            product = self.product_id.with_context(
                warehouse=self.repair_id.warehouse_id.id
            )
            product_qty = self.product_uom._compute_quantity(
                self.product_uom_qty, self.product_id.uom_id
            )
            available_qty = (
                self.env["stock.quant"]
                .search(
                    [
                        ("location_id", "child_of", self.location_id.id),
                        ("location_id.usage", "=", "internal"),
                        ("product_id", "=", self.product_id.id),
                    ]
                )
                .mapped("quantity")
            )
            if (
                float_compare(
                    product.virtual_available, product_qty, precision_digits=precision
                )
                == -1
            ):
                if available_qty and product_qty > sum(available_qty):
                    message = _(
                        "You plan to sell %s %s but you only have %s %s available in %s location."
                    ) % (
                        self.product_uom_qty,
                        self.product_uom.name,
                        sum(available_qty),
                        product.uom_id.name,
                        self.location_id.name,
                    )
                    warning_mess = {
                        "title": _("Not enough inventory!"),
                        "message": message,
                    }
                    return {"warning": warning_mess}
            if available_qty:
                self.available_qty = sum(available_qty)
        return {}

    def _action_launch_stock_rule(self):
        """
        Launch procurement group run method with required/custom fields genrated by a
        sale order line. procurement group will launch '_run_pull', '_run_buy' or '_run_manufacture'
        depending on the sale order line product rule.
        """
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        procurements = []
        buy_rule = self.env.ref("purchase_stock.route_warehouse0_buy")
        make_to_order_rule = self.env.ref("stock.route_warehouse0_mto")
        for line in self:
            if line.type != "add" or not line.product_id.type in ("consu", "product"):
                continue
            route_ids = line.product_id.route_ids.ids
            if (
                line.type == "add"
                and buy_rule
                and make_to_order_rule
                and (buy_rule.id in route_ids)
                and (make_to_order_rule.id in route_ids)
            ):
                qty = 0.0
                if line.move_id.state != "cancel":
                    qty += line.move_id.product_uom._compute_quantity(
                        line.move_id.product_uom_qty,
                        line.product_uom,
                        rounding_method="HALF-UP",
                    )
                if (
                    float_compare(qty, line.product_uom_qty, precision_digits=precision)
                    >= 0
                ):
                    continue

                product_qty = line.product_uom_qty - qty

                line_uom = line.product_uom
                quant_uom = line.product_id.uom_id
                product_qty, procurement_uom = line_uom._adjust_uom_quantities(
                    product_qty, quant_uom
                )

                date_planned = line.repair_id.create_date + timedelta(
                    days=line.product_id.sale_delay
                )
                values = {
                    "company_id": line.repair_id.company_id,
                    "date_planned": date_planned
                    or fields.Datetime.to_string(
                        fields.Datetime.now() + timedelta(days=10)
                    ),
                    "warehouse_id": line.repair_id.warehouse_id or False,
                    "partner_dest_id": line.repair_id.partner_id,
                }
                procurements.append(
                    self.env["procurement.group"].Procurement(
                        line.product_id,
                        product_qty,
                        procurement_uom,
                        line.repair_id.warehouse_id.lot_stock_id,
                        line.name,
                        line.repair_id.name,
                        line.repair_id.company_id,
                        values,
                    )
                )
        if procurements:
            self.env["procurement.group"].with_context({"is_repair_order": True}).run(
                procurements
            )
        return True
