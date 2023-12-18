# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    product_certificate_days_to_red = fields.Integer(
        related='company_id.product_certificate_days_to_red', readonly=False)
    product_certificate_days_to_yellow = fields.Integer(
        related='company_id.product_certificate_days_to_yellow', readonly=False)
    product_certificate_stage_required = fields.Boolean(
        related='company_id.product_certificate_stage_required', readonly=False)
