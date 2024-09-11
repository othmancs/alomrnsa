# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    join_work_after_vacation = fields.Boolean(
        string="Join Work After Vacation",
        config_parameter="saudi_hr_vacations.join_work_after_vacation",
    )
