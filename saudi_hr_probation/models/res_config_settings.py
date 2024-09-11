# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    probation_duration = fields.Integer(string='Probation Months', config_parameter='saudi_hr_evolution.probation_duration', default=3)
