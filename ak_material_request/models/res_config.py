# -*- coding: utf-8 -*-
# Part of Odoo, Aktiv Software PVT. LTD.
# See LICENSE file for full copyright & licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    two_step_material_req = fields.Boolean(
        related="company_id.two_step_material_req",
        readonly=False,
        string="Allow Material Request in 2-Steps",
    )
