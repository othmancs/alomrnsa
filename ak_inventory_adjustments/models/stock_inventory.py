# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.misc import OrderedSet
from odoo.tools import float_compare
import json


class StockInventory(models.Model):
    _name = "stock.inventory"
    _description = "Inventory"
    _order = "date desc, id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        "Inventory Reference",
        default="Inventory",
        readonly=True,
        required=True,
        states={"draft": [("readonly", False)]},
    )
    date = fields.Datetime(
        "Inventory Date",
        readonly=True,
        required=True,
        default=fields.Datetime.now,
        help="If the inventory adjustment is not validated, date at which the theoritical quantities have been checked.\n"
        "If the inventory adjustment is validated, date at which the inventory adjustment has been validated.",
    )
    line_ids = fields.One2many(
        "stock.inventory.line",
        "inventory_id",
        string="Inventories",
        copy=False,
        readonly=False,
        states={"done": [("readonly", True)]},
    )
    move_ids = fields.One2many(
        "stock.move",
        "inventory_id",
        string="Created Moves",
        states={"done": [("readonly", True)]},
    )
    state = fields.Selection(
        string="Status",
        selection=[
            ("draft", "Draft"),
            ("cancel", "Cancelled"),
            ("confirm", "In Progress"),
            ("done", "Validated"),
        ],
        copy=False,
        index=True,
        readonly=True,
        tracking=True,
        default="draft",
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        readonly=True,
        index=True,
        required=True,
        states={"draft": [("readonly", False)]},
        default=lambda self: self.env.company,
    )
    location_ids = fields.Many2many(
        "stock.location",
        string="Locations",
        readonly=True,
        check_company=True,
        states={"draft": [("readonly", False)]},
        domain="[('company_id', '=', company_id), ('usage', 'in', ['internal', 'transit'])]",
    )
    product_cate_ids = fields.Many2many("product.category", string="Product Category")

    @api.depends("product_cate_ids")
    def _compute_product_id_domain(self):
        for rec in self:
            domain = [
                ("type", "=", "product"),
                ("company_id", "in", [False, rec.company_id.id]),
            ]
            if rec.product_cate_ids:
                domain.append(("categ_id", "in", self.product_cate_ids.ids))
            rec.product_id_domain = json.dumps(domain)

    product_id_domain = fields.Char(
        compute="_compute_product_id_domain", readonly=True, store=False
    )
    product_ids = fields.Many2many(
        "product.product",
        string="Products",
        check_company=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        domain="[('type', '=', 'product'), ('company_id', 'in', [False, company_id])]",
        help="Specify Products to focus your inventory on particular Products.",
    )

    user_id = fields.Many2one(
        "res.users", default=lambda self: self.env.user, string="Responsible"
    )
    start_empty = fields.Boolean(
        "Empty Inventory", help="Allows to start with an empty inventory."
    )
    prefill_counted_quantity = fields.Selection(
        string="Counted Quantities",
        help="Allows to start with a pre-filled counted quantity for each lines or "
        "with all counted quantities set to zero.",
        default="counted",
        selection=[
            ("counted", "Default to stock on hand"),
            ("zero", "Default to zero"),
        ],
    )
    exhausted = fields.Boolean(
        "Include Exhausted Products",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Include also products with quantity of 0",
    )
    accounting_date = fields.Date(
        "Accounting Date",
        help="Date at which the accounting entries will be created"
        " in case of automated inventory valuation."
        " If empty, the inventory date will be used.",
    )
    has_account_moves = fields.Boolean(
        compute="_compute_has_account_moves", compute_sudo=True
    )

    @api.onchange("product_cate_ids")
    def onchange_categ_id(self):
        """ Update domain as category change """
        domain = [
            ("type", "=", "product"),
            ("company_id", "in", [False, self.company_id.id]),
        ]
        if self.product_cate_ids:
            domain.append(("categ_id", "in", self.product_cate_ids.ids))
        return {"domain": {"product_ids": domain}}

    def _compute_has_account_moves(self):
        """ count account moves """
        for inventory in self:
            inventory.has_account_moves = False
            if inventory.state == "done" and inventory.move_ids:
                account_move = self.env["account.move"].search_count(
                    [("stock_move_id.id", "in", inventory.move_ids.ids)]
                )
                inventory.has_account_moves = account_move > 0

    def action_get_account_moves(self):
        self.ensure_one()
        action_data = self.env["ir.actions.act_window"]._for_xml_id(
            "account.action_move_journal_line"
        )
        action_data.update(
            {
                "domain": [("stock_move_id.id", "in", self.move_ids.ids)],
                "context": dict(self._context, create=False),
            }
        )
        return action_data

    @api.onchange("company_id")
    def _onchange_company_id(self):
        # If the multilocation group is not active, default the location to the one of the main
        # warehouse.
        if not self.user_has_groups("stock.group_stock_multi_locations"):
            warehouse = self.env["stock.warehouse"].search(
                [("company_id", "=", self.company_id.id)], limit=1
            )
            if warehouse:
                self.location_ids = warehouse.lot_stock_id

    def copy_data(self, default=None):
        name = _("%s (copy)") % (self.name)
        default = dict(default or {}, name=name)
        return super(StockInventory, self).copy_data(default)

    def unlink(self):
        for inventory in self:
            if inventory.state not in ("draft", "cancel") and not self.env.context.get(
                MODULE_UNINSTALL_FLAG, False
            ):
                raise UserError(
                    _(
                        "You can only delete a draft inventory adjustment. If the inventory adjustment is not done, you can cancel it."
                    )
                )
        return super(StockInventory, self).unlink()

    def action_validate(self):
        if not self.exists():
            return
        self.ensure_one()
        if self.state != "confirm":
            raise UserError(
                _(
                    "You can't validate the inventory '%s', maybe this inventory "
                    "has been already validated or isn't ready.",
                    self.name,
                )
            )
        products_tracked_without_lot = []
        for quant in self.line_ids:
            rounding = quant.product_uom_id.rounding
            if (
                fields.Float.is_zero(quant.difference_qty, precision_rounding=rounding)
                and fields.Float.is_zero(quant.product_qty, precision_rounding=rounding)
                and fields.Float.is_zero(
                    quant.theoretical_qty, precision_rounding=rounding
                )
            ):
                continue
            if (
                quant.product_id.tracking in ["lot", "serial"]
                and not quant.prod_lot_id
                and quant.product_qty != quant.theoretical_qty
                and not quant.theoretical_qty
            ):
                products_tracked_without_lot.append(quant.product_id.id)
        inventory_lines = self.line_ids.filtered(
            lambda l: l.product_id.tracking in ["lot", "serial"]
            and not l.prod_lot_id
            and l.theoretical_qty != l.product_qty
        )
        lines = self.line_ids.filtered(
            lambda l: float_compare(
                l.product_qty, 1, precision_rounding=l.product_uom_id.rounding
            )
            > 0
            and l.product_id.tracking == "serial"
            and l.prod_lot_id
        )
        ctx = self.env.context.copy()
        ctx.update(
            {
                "stock_inventory": True,
                "default_product_ids": inventory_lines.mapped("product_id").ids,
                "default_inventory_id": self.id,
            }
        )
        if inventory_lines and not lines:

            return {
                "name": _("Tracked Products in Inventory Adjustment"),
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "views": [(False, "form")],
                "res_model": "stock.track.confirmation",
                "target": "new",
                "context": ctx,
            }
        self._action_done()
        self.line_ids._check_company()
        self._check_company()

    def _action_done(self):
        negative = next(
            (
                line
                for line in self.mapped("line_ids")
                if line.product_qty < 0 and line.product_qty != line.theoretical_qty
            ),
            False,
        )
        if negative:
            raise UserError(
                _(
                    "You cannot set a negative product quantity in an inventory line:\n\t%s - qty: %s",
                    negative.product_id,
                    negative.product_qty,
                )
            )
        self.action_check()
        self.write({"state": "done", "date": fields.Datetime.now()})
        self.post_inventory()
        return True

    def post_inventory(self):
        # The inventory is posted as a single step which means quants cannot be moved from an internal location to another using an inventory
        # as they will be moved to inventory loss, and other quants will be created to the encoded quant location. This is a normal behavior
        # as quants cannot be reuse from inventory location (users can still manually move the products before/after the inventory if they want).
        acc_inventories = self.filtered(lambda inventory: inventory.accounting_date)
        for inventory in acc_inventories:
            self.with_context(force_period_date=inventory.accounting_date).mapped(
                "move_ids"
            ).filtered(lambda move: move.state != "done")._action_done()
        other_inventories = self - acc_inventories
        if other_inventories:
            self.mapped("move_ids").filtered(
                lambda move: move.state != "done"
            )._action_done()
        return True

    def action_check(self):
        """ Checks the inventory and computes the stock move to do """
        for inventory in self.filtered(lambda x: x.state not in ("done", "cancel")):
            # first remove the existing stock moves linked to this inventory
            inventory.with_context(prefetch_fields=False).mapped("move_ids").unlink()
            inventory.line_ids._generate_moves()

    def action_cancel_draft(self):
        self.mapped("move_ids")._action_cancel()
        self.line_ids.unlink()
        self.write({"state": "draft"})

    def action_start(self):
        self.ensure_one()
        self._action_start()
        self._check_company()
        return self.action_open_inventory_lines()

    def _action_start(self):
        """ Confirms the Inventory Adjustment and generates its inventory lines
        if its state is draft and don't have already inventory lines (can happen
        with demo data or tests).
        """
        for inventory in self:
            if inventory.state != "draft":
                continue
            vals = {"state": "confirm", "date": fields.Datetime.now()}
            if not inventory.line_ids and not inventory.start_empty:
                self.env["stock.inventory.line"].create(
                    inventory._get_inventory_lines_values()
                )
            inventory.write(vals)

    def action_open_inventory_lines(self):
        self.ensure_one()
        action = {
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "name": _("Inventory Lines"),
            "res_model": "stock.inventory.line",
        }
        context = {
            "default_is_editable": True,
            "default_inventory_id": self.id,
            "default_company_id": self.company_id.id,
        }
        # Define domains and context
        domain = [
            ("inventory_id", "=", self.id),
            ("location_id.usage", "in", ["internal", "transit"]),
        ]
        if self.location_ids:
            context["default_location_id"] = self.location_ids[0].id
            if len(self.location_ids) == 1 and not self.location_ids[0].child_ids:
                context["readonly_location_id"] = True
        # no product_ids => we're allowed to create new products in tree
        action["view_id"] = self.env.ref(
            "ak_inventory_adjustments.stock_inventory_line_tree"
        ).id
        if self.product_ids:
            # no_create on product_id field
            action["view_id"] = self.env.ref(
                "ak_inventory_adjustments.stock_inventory_line_tree_no_product_create"
            ).id
            if len(self.product_ids) == 1:
                context["default_product_id"] = self.product_ids[0].id
        action.update({"context": context, "domain": domain})
        return action

    def action_view_related_move_lines(self):
        self.ensure_one()
        action = {
            "name": _("Product Moves"),
            "type": "ir.actions.act_window",
            "res_model": "stock.move.line",
            "view_type": "list",
            "view_mode": "list,form",
            "domain": [("move_id", "in", self.move_ids.ids)],
        }
        return action

    def action_print(self):
        return self.env.ref(
            "ak_inventory_adjustments.action_report_inventory_custom"
        ).report_action(self)

    def _get_quantities(self):
        """Return quantities group by product_id, location_id, lot_id, package_id and owner_id

        :return: a dict with keys as tuple of group by and quantity as value
        :rtype: dict
        """
        self.ensure_one()
        if self.location_ids:
            domain_loc = [("id", "child_of", self.location_ids.ids)]
        else:
            domain_loc = [
                ("company_id", "=", self.company_id.id),
                ("usage", "in", ["internal", "transit"]),
            ]
        locations_ids = [
            l["id"] for l in self.env["stock.location"].search_read(domain_loc, ["id"])
        ]

        domain = [
            ("company_id", "=", self.company_id.id),
            ("quantity", "!=", "0"),
            ("location_id", "in", locations_ids),
        ]
        if self.prefill_counted_quantity == "zero":
            domain.append(("product_id.active", "=", True))

        if self.product_ids:
            domain = expression.AND(
                [domain, [("product_id", "in", self.product_ids.ids)]]
            )
        if self.product_cate_ids:
            domain = expression.AND(
                [domain, [("product_categ_id", "in", self.product_cate_ids.ids)]]
            )

        fields = [
            "product_id",
            "location_id",
            "lot_id",
            "package_id",
            "owner_id",
            "quantity:sum",
        ]
        group_by = ["product_id", "location_id", "lot_id", "package_id", "owner_id"]
        quants = self.env["stock.quant"].read_group(
            domain, fields, group_by, lazy=False
        )
        return {
            (
                quant.get("product_id") and quant.get("product_id")[0] or False,
                quant.get("location_id") and quant.get("location_id")[0] or False,
                quant.get("lot_id") and quant.get("lot_id")[0] or False,
                quant.get("package_id") and quant.get("package_id")[0] or False,
                quant.get("owner_id") and quant.get("owner_id")[0] or False,
            ): quant.get("quantity")
            for quant in quants
        }

    def _get_exhausted_inventory_lines_vals(self, non_exhausted_set):
        """Return the values of the inventory lines to create if the user
        wants to include exhausted products. Exhausted products are products
        without quantities or quantity equal to 0.

        :param non_exhausted_set: set of tuple (product_id, location_id) of non exhausted product-location
        :return: a list containing the `stock.inventory.line` values to create
        :rtype: list
        """
        self.ensure_one()
        if self.product_ids:
            product_ids = self.product_ids.ids
        else:
            product_ids = self.env["product.product"].search_read(
                [
                    "|",
                    ("company_id", "=", self.company_id.id),
                    ("company_id", "=", False),
                    ("type", "=", "product"),
                    ("active", "=", True),
                ],
                ["id"],
            )
            product_ids = [p["id"] for p in product_ids]

        if self.location_ids:
            location_ids = self.location_ids.ids
        else:
            location_ids = (
                self.env["stock.warehouse"]
                .search([("company_id", "=", self.company_id.id)])
                .lot_stock_id.ids
            )

        vals = []
        for product_id in product_ids:
            for location_id in location_ids:
                if (product_id, location_id) not in non_exhausted_set:
                    vals.append(
                        {
                            "inventory_id": self.id,
                            "product_id": product_id,
                            "location_id": location_id,
                            "theoretical_qty": 0,
                        }
                    )
        return vals

    def _get_inventory_lines_values(self):
        """Return the values of the inventory lines to create for this inventory.

        :return: a list containing the `stock.inventory.line` values to create
        :rtype: list
        """
        self.ensure_one()
        quants_groups = self._get_quantities()
        vals = []
        product_ids = OrderedSet()
        for (
            (product_id, location_id, lot_id, package_id, owner_id),
            quantity,
        ) in quants_groups.items():
            line_values = {
                "inventory_id": self.id,
                "product_qty": 0
                if self.prefill_counted_quantity == "zero"
                else quantity,
                "theoretical_qty": quantity,
                "prod_lot_id": lot_id,
                "partner_id": owner_id,
                "product_id": product_id,
                "location_id": location_id,
                "package_id": package_id,
            }
            product_ids.add(product_id)
            vals.append(line_values)
        product_id_to_product = dict(
            zip(product_ids, self.env["product.product"].browse(product_ids))
        )
        for val in vals:
            val["product_uom_id"] = product_id_to_product[
                val["product_id"]
            ].product_tmpl_id.uom_id.id
        if self.exhausted:
            vals += self._get_exhausted_inventory_lines_vals(
                {(l["product_id"], l["location_id"]) for l in vals}
            )
        return vals
