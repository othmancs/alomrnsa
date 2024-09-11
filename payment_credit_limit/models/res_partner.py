# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    remaining_credit_limit = fields.Float("Remaining Credit Limit", compute="get_remaining_credit_limit",
                                          store=False, help="Remaining Credit Limit Amount")

    def get_remaining_credit_limit(self):
        for record in self:
            if record.credit_limit:
                record.remaining_credit_limit = record.credit_limit - sum(record.invoice_ids.filtered(lambda inv: inv.state in ["draft", "posted"]).mapped("amount_residual"))
            else:
                record.remaining_credit_limit = 0.0
