# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'

    product_certificate_days_to_red = fields.Integer(
        string='Days to Red', default=30,
        help="Days needed to mark product Certificates in Red.")
    product_certificate_days_to_yellow = fields.Integer(
        string='Days to Yellow', default=60,
        help="Days needed to mark product Certificates in Yellow.")
    product_certificate_stage_required = fields.Boolean(
        string='Staging Required',
        help="Makes the selection of a stage mandatory when creating product certificates.")

    @api.constrains('product_certificate_days_to_red', 'product_certificate_days_to_yellow')
    def _check_valid_certificate_days(self):
        for company in self:
            if company.product_certificate_days_to_yellow <= company.product_certificate_days_to_red:
                raise ValidationError("The Yellow Days must be greater than the Red Days.")
