# -*- coding: utf-8 -*-

from odoo import fields, models, api,_

class ProductTemplate(models.Model):
    _inherit = "product.template"

    web_pro_name = fields.Char(string="Website Product Name", translate=True, index=True)