# -- coding: utf-8 --
#################################################################################
# Author      : Plus Technology Co.Ltd. (<https://www.plustech-it.com//>)
# Copyright(c): 2024-Plus Technology Co. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
#################################################################################
from odoo import api, fields, models


class SaleProductsReport(models.Model):
    _name = "sale.products.report"
    _description = "Product Sales Report"
    _order = 'total_price_total desc'

    product_id = fields.Many2one('product.product', string='Product')
    total_price_subtotal = fields.Float('Subtotal')
    total_discount_amount = fields.Float('Discount Amount')
    total_price_total = fields.Float('Total')
    total_tax_amount = fields.Float('Tax Amount')
    total_quantity = fields.Float('Total Quantity')
    list_price = fields.Float('List Price')
    refund_total_price_total = fields.Float('Refund Total')
    refund_quantity = fields.Float('Refund Quantity')
