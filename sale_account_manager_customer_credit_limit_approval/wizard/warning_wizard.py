# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields


class WarningWizard(models.TransientModel):
    _name = "warning.wizard"
    _description = "Warning Wizard"

    def get_default(self):
        if self.env.context.get("message", False):
            return self.env.context.get("message")
        return False

    name = fields.Text(string="Message", readonly=True, default=get_default)
    sale_id = fields.Many2one('sale.order', string="Sale Order")

    def action_confirm(self):
        self.sale_id.with_context(warning=True).action_confirm()
