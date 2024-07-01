# -*- coding: utf-8 -*-
# Email:smartthinkerstechne@gmail.com

{
    'name': 'Set Product Minimum or Maximum Price',
    'author': 'smartthinkerstechne@gmail.com',
    "license": "LGPL-3",   
    'support': 'smartthinkerstechne@gmail.com',
    'version': '16.0.1',
    'category': 'Sales',
    'summary': "Set Product Minimum or Maximum Sales Price Point Of Sale Product Min Price and Max Price Odoo",
    'description': """This Module "Minimum and Maximum Product Price Base" is the base module for the "Minimum and Maximum Product Price" modules.""",
    "depends": ["base_setup", "product","sale_management"],
    "data": [
        'security/price_security.xml',
        'views/product_template_views.xml',
    ],
    "images": ["static/description/banner.gif",],
    "installable": True,
    "auto_install": False,
    "application": True,   
}