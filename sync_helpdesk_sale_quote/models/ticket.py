# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import _, fields, models
from odoo.exceptions import UserError


class Ticket(models.Model):
    _inherit = "ticket.ticket"

    def _quotation_count(self):
        """
        Count sales order depends on ticket
        """
        for ticket in self:
            ticket.sale_count = (
                len(ticket.sale_quotation_ids) if ticket.sale_quotation_ids else 0.0
            )

    sale_count = fields.Integer(
        compute="_quotation_count", string="#Quotations", copy=False
    )
    sale_quotation_ids = fields.One2many(
        "sale.order", "ticket_id", string="Quotations", copy=False
    )

    def view_quotations(self):
        """
        Show sales order
        """
        self.ensure_one()
        if not self.partner_id:
            raise UserError(_("Please select customer for create quotation!"))
        form_view = self.env.ref("sale.view_order_form")
        tree_view = self.env.ref("sale.view_quotation_tree")
        context = dict(self.env.context)
        context.update(
            {
                "default_partner_id": self.partner_id.id,
                "default_date_order": fields.Datetime.now(),
                "default_ticket_id": self.id,
            }
        )
        return {
            "name": "Quotation",
            "view_mode": "form",
            "res_model": "sale.order",
            "views": [(tree_view.id, "tree"), (form_view.id, "form")],
            "domain": [("ticket_id", "=", self.id)],
            "type": "ir.actions.act_window",
            "target": "current",
            "context": context,
            "nodestroy": True,
        }
