# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import fields, models


class ShOederType(models.Model):
    _name = 'sh.order.type'
    _description = 'Base order type'

    name = fields.Char(string='Name')
    img = fields.Image('Image', max_width=200, max_height=200)
    is_home_delivery = fields.Boolean('Is Home Delivery?')
