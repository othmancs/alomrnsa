# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_enable_stock_into_orderline = fields.Boolean(
        "Visible Stock Info. in Order Line?",
        implied_group='sale_product_stock_info.group_enable_stock_into_orderline',
        help="Enable this configuration to you can see the warehouse/Location wise Stock into Sale Order Line.")
    order_line_stock_type = fields.Selection([
        ('warehouse_wise', 'Warehouse Wise'),
        ('location_wise', 'Location Wise')], string="Stock Info. Type",
        config_parameter='sale_product_stock_info.order_line_stock_type',
        help="Based on selected Type stock will be show into sale order line.")
