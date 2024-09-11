# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    account_manager = fields.Boolean("Account Manager", config_parameter="saudi_hr_job_requisition.account_manager")
