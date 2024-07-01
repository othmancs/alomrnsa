# -*- coding: utf-8 -*-
# Email:smartthinkerstechne@gmail.com

from odoo import fields, models


# Product Template
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    st_pro_min_sale_price = fields.Float(string="Minimum Sales Price")
    st_pro_max_sale_price = fields.Float(string="Maximum Sales Price")  