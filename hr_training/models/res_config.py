# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    expire_training_notification_days = fields.Integer(string='Training Notification Before Days',
        config_parameter='hr_training.expire_training_notification_days', default='1')
