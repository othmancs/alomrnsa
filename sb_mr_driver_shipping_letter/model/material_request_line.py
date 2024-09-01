# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.api import onchange


class MRLine(models.Model):
    _inherit = "material.request.line"

    seq = fields.Integer(string="التسلسل", required=False, )
    product_ref= fields.Integer(string="الكود", required=False, )
    product_ref_2= fields.Char(string="الكود", compute="_compute_product_ref_2", required=False, store='1')


    @api.onchange('product_id')
    def _compute_product_ref_2(self):
        for rec in self:
            rec.product_ref_2 = rec.product_id.default_code



