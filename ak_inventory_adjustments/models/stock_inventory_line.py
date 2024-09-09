# -*- coding: utf-8 -*-
import json

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero


class InventoryLine(models.Model):
    _name = "stock.inventory.line"
    _description = "Inventory Line"
    _order = "product_id, inventory_id, location_id, prod_lot_id"

    @api.model
    def _domain_location_id(self):
        if self.env.context.get("active_model") == "stock.inventory":
            inventory = self.env["stock.inventory"].browse(
                self.env.context.get("active_id")
            )
            if inventory.exists() and inventory.location_ids:
                return (
                    "[('company_id', '=', company_id), ('usage', 'in', ['internal', 'transit']), ('id', 'child_of', %s)]"
                    % inventory.location_ids.ids
                )
        return "[('company_id', '=', company_id), ('usage', 'in', ['internal', 'transit'])]"

    @api.depends("inventory_id.product_ids", "inventory_id.product_cate_ids")
    def _compute_product_id_domain(self):
        if self.env.context.get("active_model") == "stock.inventory":
            inventory = self.env["stock.inventory"].browse(
                self.env.context.get("active_id")
            )
            domain = [
                ("type", "=", "product"),
                "|",
                ("company_id", "=", False),
                ("company_id", "=", inventory.company_id.id),
            ]
            if inventory.exists():
                if len(inventory.product_ids) >= 1:
                    domain.append(("id", "in", inventory.product_ids.ids))
                if len(inventory.product_cate_ids) >= 1:
                    domain.append(("categ_id", "in", inventory.product_cate_ids.ids))

                self.product_id_domain = json.dumps(domain)

    is_editable = fields.Boolean(help="Technical field to restrict editing.")
    inventory_id = fields.Many2one(
        "stock.inventory",
        "Inventory",
        check_company=True,
        index=True,
        ondelete="cascade",
    )
    partner_id = fields.Many2one("res.partner", "Owner", check_company=True)
    product_id = fields.Many2one(
        "product.product", "Product", check_company=True, index=True, required=True
    )
    product_id_domain = fields.Char(
        compute="_compute_product_id_domain", readonly=True, store=False
    )
    product_uom_id = fields.Many2one(
        "uom.uom", "Product Unit of Measure", required=True
    )
    product_qty = fields.Float(
        "Counted Quantity",
        readonly=True,
        states={
            "confirm": [("readonly", False)],
            "waiting_for_approval": [("readonly", False)],
        },
        digits="Product Unit of Measure",
        default=0,
    )
    categ_id = fields.Many2one(related="product_id.categ_id", store=True)
    package_id = fields.Many2one(
        "stock.quant.package", "Pack", index=True, check_company=True
    )
    package_id_domain = fields.Char(
        compute="_compute_package_id_domain", readonly=True, store=False
    )

    @api.depends("location_id")
    def _compute_package_id_domain(self):
        for rec in self:
            rec.package_id_domain = []
            if rec.location_id:
                rec.package_id_domain = json.dumps(
                    [("location_id", "=", rec.location_id.id)]
                )

    location_id = fields.Many2one(
        "stock.location",
        "Location",
        check_company=True,
        domain=lambda self: self._domain_location_id(),
        index=True,
        required=True,
    )
    prod_lot_id = fields.Many2one(
        "stock.lot",
        "Lot/Serial Number",
        check_company=True,
        domain="[('product_id','=',product_id), ('company_id', '=', company_id)]",
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        related="inventory_id.company_id",
        index=True,
        readonly=True,
        store=True,
    )
    state = fields.Selection(string="Status", related="inventory_id.state")
    theoretical_qty = fields.Float(
        "Theoretical Quantity", digits="Product Unit of Measure", readonly=True
    )
    difference_qty = fields.Float(
        "Difference",
        compute="_compute_difference",
        help="Indicates the gap between the product's theoretical quantity and its newest quantity.",
        readonly=True,
        digits="Product Unit of Measure",
        search="_search_difference_qty",
    )
    inventory_date = fields.Datetime(
        "Inventory Date",
        readonly=True,
        default=fields.Datetime.now,
        help="Last date at which the On Hand Quantity has been computed.",
    )
    outdated = fields.Boolean(
        string="Quantity outdated",
        compute="_compute_outdated",
        search="_search_outdated",
    )
    product_tracking = fields.Selection(
        string="Tracking", related="product_id.tracking", readonly=True
    )

    def _get_move_values(self, qty, location_id, location_dest_id, out):
        self.ensure_one()
        return {
            "name": _("INV:") + (self.inventory_id.name or ""),
            "product_id": self.product_id.id,
            "product_uom": self.product_uom_id.id,
            "product_uom_qty": qty,
            "date": self.inventory_id.date,
            "company_id": self.inventory_id.company_id.id,
            "inventory_id": self.inventory_id.id,
            "state": "confirmed",
            "is_inventory": True,
            "restrict_partner_id": self.partner_id.id,
            "location_id": location_id,
            "location_dest_id": location_dest_id,
            "move_line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": self.product_id.id,
                        "lot_id": self.prod_lot_id.id,
                        "reserved_uom_qty": 0,  # bypass reservation here
                        "product_uom_id": self.product_uom_id.id,
                        "qty_done": qty,
                        "package_id": out and self.package_id.id or False,
                        "result_package_id": (not out) and self.package_id.id or False,
                        "location_id": location_id,
                        "location_dest_id": location_dest_id,
                        "owner_id": self.partner_id.id,
                    },
                )
            ],
        }

    def _generate_moves(self):
        vals_list = []
        for line in self:
            virtual_location = line._get_virtual_location()
            rounding = line.product_id.uom_id.rounding
            if float_is_zero(line.difference_qty, precision_rounding=rounding):
                continue
            if line.difference_qty > 0:  # found more than expected
                vals = line._get_move_values(
                    line.difference_qty, virtual_location.id, line.location_id.id, False
                )
            else:
                vals = line._get_move_values(
                    abs(line.difference_qty),
                    line.location_id.id,
                    virtual_location.id,
                    True,
                )
            vals_list.append(vals)
        return self.env["stock.move"].create(vals_list)

    @api.depends("product_qty", "theoretical_qty")
    def _compute_difference(self):
        for line in self:
            line.difference_qty = line.product_qty - line.theoretical_qty

    @api.depends(
        "inventory_date",
        "product_id.stock_move_ids",
        "theoretical_qty",
        "product_uom_id.rounding",
    )
    def _compute_outdated(self):
        quants_by_inventory = {
            inventory: inventory._get_quantities() for inventory in self.inventory_id
        }
        for line in self:
            quants = quants_by_inventory[line.inventory_id]
            if line.state == "done" or not line.id:
                line.outdated = False
                continue
            qty = quants.get(
                (
                    line.product_id.id,
                    line.location_id.id,
                    line.prod_lot_id.id,
                    line.package_id.id,
                    line.partner_id.id,
                ),
                0,
            )
            line.outdated = False
            if (
                float_compare(
                    qty,
                    line.theoretical_qty,
                    precision_rounding=line.product_uom_id.rounding,
                )
                != 0
            ):
                line.outdated = True

    @api.onchange(
        "product_id",
        "location_id",
        "product_uom_id",
        "prod_lot_id",
        "partner_id",
        "package_id",
    )
    def _onchange_quantity_context(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id
        theoretical_qty = 0
        if (
            self.product_id
            and self.location_id
            and self.product_id.uom_id.category_id == self.product_uom_id.category_id
        ):  # TDE FIXME: last part added because crash
            theoretical_qty = self.product_id.get_theoretical_quantity(
                self.product_id.id,
                self.location_id.id,
                lot_id=self.prod_lot_id.id,
                package_id=self.package_id.id,
                owner_id=self.partner_id.id,
                to_uom=self.product_uom_id.id,
            )
        # Sanity check on the lot.
        if self.prod_lot_id and (
            self.product_id.tracking == "none"
            or self.product_id != self.prod_lot_id.product_id
        ):
            self.prod_lot_id = False

        if self.prod_lot_id and self.product_id.tracking == "serial":
            # We force `product_qty` to 1 for SN tracked product because it's
            # the only relevant value aside 0 for this kind of product.
            self.product_qty = 1
        elif (
            self.product_id
            and float_compare(
                self.product_qty,
                self.theoretical_qty,
                precision_rounding=self.product_uom_id.rounding,
            )
            == 0
        ):
            # We update `product_qty` only if it equals to `theoretical_qty` to
            # avoid to reset quantity when user manually set it.
            self.product_qty = theoretical_qty
        self.theoretical_qty = theoretical_qty

    @api.model_create_multi
    def create(self, vals_list):
        """ Override to handle the case we create inventory line without
        `theoretical_qty` because this field is usually computed, but in some
        case (typicaly in tests), we create inventory line without trigger the
        onchange, so in this case, we set `theoretical_qty` depending of the
        product's theoretical quantity.
        Handles the same problem with `product_uom_id` as this field is normally
        set in an onchange of `product_id`.
        Finally, this override checks we don't try to create a duplicated line.
        """
        products = self.env["product.product"].browse(
            [vals.get("product_id") for vals in vals_list]
        )
        for product, values in zip(products, vals_list):
            if "theoretical_qty" not in values:
                theoretical_qty = self.env["product.product"].get_theoretical_quantity(
                    values["product_id"],
                    values["location_id"],
                    lot_id=values.get("prod_lot_id"),
                    package_id=values.get("package_id"),
                    owner_id=values.get("partner_id"),
                    to_uom=values.get("product_uom_id"),
                )
                values["theoretical_qty"] = theoretical_qty
            if "product_id" in values and "product_uom_id" not in values:
                values["product_uom_id"] = product.product_tmpl_id.uom_id.id
        res = super(InventoryLine, self).create(vals_list)
        res._check_no_duplicate_line()
        return res

    def write(self, vals):
        res = super(InventoryLine, self).write(vals)
        self._check_no_duplicate_line()
        return res

    def _check_no_duplicate_line(self):
        domain = [
            ("product_id", "in", self.product_id.ids),
            ("location_id", "in", self.location_id.ids),
            "|",
            ("partner_id", "in", self.partner_id.ids),
            ("partner_id", "=", None),
            "|",
            ("package_id", "in", self.package_id.ids),
            ("package_id", "=", None),
            "|",
            ("prod_lot_id", "in", self.prod_lot_id.ids),
            ("prod_lot_id", "=", None),
            "|",
            ("inventory_id", "in", self.inventory_id.ids),
            ("inventory_id", "=", None),
        ]
        groupby_fields = [
            "product_id",
            "location_id",
            "partner_id",
            "package_id",
            "prod_lot_id",
            "inventory_id",
        ]
        lines_count = {}
        for group in self.read_group(
            domain, ["product_id"], groupby_fields, lazy=False
        ):
            key = tuple([group[field] and group[field][0] for field in groupby_fields])
            lines_count[key] = group["__count"]
        for line in self:
            key = (
                line.product_id.id,
                line.location_id.id,
                line.partner_id.id,
                line.package_id.id,
                line.prod_lot_id.id,
                line.inventory_id.id,
            )
            if lines_count[key] > 1:
                raise UserError(
                    _(
                        "There is already one inventory adjustment line for this product,"
                        " you should rather modify this one instead of creating a new one."
                    )
                )

    @api.constrains("product_id")
    def _check_product_id(self):
        """ As no quants are created for consumable products, it should not be possible do adjust
        their quantity.
        """
        for line in self:
            if line.product_id.type != "product":
                raise ValidationError(
                    _("You can only adjust storable products.")
                    + "\n\n%s -> %s" % (line.product_id, line.product_id.type)
                )

    def _get_virtual_location(self):
        return self.product_id.with_company(self.company_id).property_stock_inventory

    def action_refresh_quantity(self):
        filtered_lines = self.filtered(lambda l: l.state != "done")
        for line in filtered_lines:
            if line.outdated:
                quants = self.env["stock.quant"]._gather(
                    line.product_id,
                    line.location_id,
                    lot_id=line.prod_lot_id,
                    package_id=line.package_id,
                    owner_id=line.partner_id,
                    strict=True,
                )
                line.theoretical_qty = 0
                if quants.exists():
                    quantity = sum(quants.mapped("quantity"))
                    if line.theoretical_qty != quantity:
                        line.theoretical_qty = quantity
                line.inventory_date = fields.Datetime.now()

    def action_reset_product_qty(self):
        """ Write `product_qty` to zero on the selected records. """
        impacted_lines = self.env["stock.inventory.line"]
        for line in self:
            if line.state == "done":
                continue
            impacted_lines |= line
        impacted_lines.write({"product_qty": 0})

    def _search_difference_qty(self, operator, value):
        if operator == "=":
            result = True
        elif operator == "!=":
            result = False
        else:
            raise NotImplementedError()
        if not self.env.context.get("default_inventory_id"):
            raise NotImplementedError(
                _(
                    "Unsupported search on %s outside of an Inventory Adjustment",
                    "difference_qty",
                )
            )
        lines = self.search(
            [("inventory_id", "=", self.env.context.get("default_inventory_id"))]
        )
        line_ids = lines.filtered(
            lambda line: float_is_zero(
                line.difference_qty, precision_rounding=line.product_id.uom_id.rounding
            )
            == result
        ).ids
        return [("id", "in", line_ids)]

    def _search_outdated(self, operator, value):
        if operator != "=":
            if operator == "!=" and isinstance(value, bool):
                value = not value
            else:
                raise NotImplementedError()
        if not self.env.context.get("default_inventory_id"):
            raise NotImplementedError(
                _(
                    "Unsupported search on %s outside of an Inventory Adjustment",
                    "outdated",
                )
            )
        lines = self.search(
            [("inventory_id", "=", self.env.context.get("default_inventory_id"))]
        )
        line_ids = lines.filtered(lambda line: line.outdated == value).ids
        return [("id", "in", line_ids)]
