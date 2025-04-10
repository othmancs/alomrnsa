# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # يمكنك إضافة حقول مخصصة هنا إذا لزم الأمر
    custom_field = fields.Char(string='حقل مخصص')