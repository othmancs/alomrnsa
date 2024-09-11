# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    clearance_mandatory_for_eos = fields.Boolean(
        "Clearance Mandatory for EOS",
        config_parameter="saudi_hr_eos.clearance_mandatory_for_eos",
    )
