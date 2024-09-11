# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    hr_id = fields.Many2one('hr.employee', string='HR', config_parameter='saudi_hr.hr_id')
    enrolled_months = fields.Integer(string='Enrolling Duration', config_parameter='saudi_hr.enrolled_months', default=6)
