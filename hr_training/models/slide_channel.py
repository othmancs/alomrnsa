# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class SlideChannel(models.Model):
    _inherit = 'slide.channel'

    training_topic_id = fields.Many2one('training.topic', string='Topic')
    training_method_id = fields.Many2one('training.method', string='Method')
