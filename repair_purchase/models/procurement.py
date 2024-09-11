# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero

_logger = logging.getLogger(__name__)


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def run(self, procurements, raise_user_error=False):
        ctx = dict(self._context)
        if ctx.get("is_repair_order"):
            actions_to_run = defaultdict(list)
            errors = []
            for procurement in procurements:
                procurement.values.setdefault("company_id", self.env.company)
                procurement.values.setdefault("priority", "1")
                procurement.values.setdefault("date_planned", fields.Datetime.now())
                if procurement.product_id.type not in (
                    "consu",
                    "product",
                ) or float_is_zero(
                    procurement.product_qty,
                    precision_rounding=procurement.product_uom.rounding,
                ):
                    continue
                rule = self._get_rule(
                    procurement.product_id, procurement.location_id, procurement.values
                )
                if not rule:
                    errors.append(
                        _(
                            'No rule has been found to replenish "%s" in "%s".\nVerify the routes configuration on the product.'
                        )
                        % (
                            procurement.product_id.display_name,
                            procurement.location_id.display_name,
                        )
                    )
                else:
                    action = "pull" if rule.action == "pull_push" else rule.action
                    if action == "buy":
                        product_qty = procurement.product_qty or 0.0
                        available_qty = float(
                            sum(
                                self.env["stock.quant"]
                                .search(
                                    [
                                        (
                                            "location_id",
                                            "child_of",
                                            procurement.location_id.id,
                                        ),
                                        ("location_id.usage", "=", "internal"),
                                        ("product_id", "=", procurement.product_id.id),
                                    ]
                                )
                                .mapped("quantity")
                            )
                        )
                        if available_qty < product_qty:
                            product_qty = product_qty - available_qty
                            procurement.values.setdefault("product_qty", product_qty)
                        else:
                            return True
                    actions_to_run[action].append((procurement, rule))

            if errors:
                raise UserError("\n".join(errors))

            for action, procurements in actions_to_run.items():
                if hasattr(self.env["stock.rule"], "_run_%s" % action):
                    try:
                        getattr(self.env["stock.rule"], "_run_%s" % action)(
                            procurements
                        )
                    except UserError as e:
                        errors.append(e.name)
                else:
                    _logger.error(
                        "The method _run_%s doesn't exist on the procurement rules"
                        % action
                    )

            if errors:
                raise UserError("\n".join(errors))
            return True
        else:
            return super(ProcurementGroup, self).run(
                procurements=procurements, raise_user_error=raise_user_error
            )
