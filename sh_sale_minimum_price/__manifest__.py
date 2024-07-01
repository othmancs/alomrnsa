# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Sale Order Restrict Lower Price Than Pricelist Price | Restrict Less Sale Order Price Based On Pricelist | Sale Minimum Price",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "license": "OPL-1",
    "support": "support@softhealer.com",
    "version": "16.0.1",
    "category": "Sales",
    "summary": "Sales Minimum Price, Sale Order Minimum Price,Product Pricelist,Pricelist Management,Product Minimum Price,Min Product price,Product Selling Price,Product Minimum Selling Price,Minimum Sale Price,Minimum Unit Price,Unit Price On Pricelist Odoo",
    "description": """This module allows to set the minimum unit price on the product pricelist. When the unit price is lower than the minimum price you can not confirm the quotation/ sale order. So here sales department can move quotations without requiring the manager's approval at each step.""",
    "depends": ["sale_management"],
    "data": [
        "security/sale_order_groups.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
    'images': ['static/description/background.png', ],
    "price": 35,
    "currency": "EUR"
}
