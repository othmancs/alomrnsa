# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sales Multi Pricelist',
    'version': '16.0.0.0',
    'category': 'Sales',
    'summary': 'Sales Multi Pricelists sale multi pricelists sale multiple pricelist on Sales order Multi Pricelist on sale order multi pricelist sale multiple pricelist for sales pricelist allow multi pricelist on sales different product pricelist on products pricelist',
    'description' :"""
        
        Sale Order Multiple Pricelist in odoo,
        Sale Multi Pricelist in odoo,
        Different Pricelist for Each Product in odoo,
        Different Pricelist for Each Order Line in odoo,
        Select Pricelist for Product in odoo,
        Pricelist for Sale Order Line in odoo,
    
    """,
    'author': 'BrowseInfo',
    "price": 15,
    "currency": 'EUR',
    'website': 'https://www.browseinfo.in',
    'depends': ['base','sale_management','product'],
    'data': [
        'security/ir.model.access.csv',
        'views/models_view.xml',
        'wizard/sale_order_pricelist_update_wizard.xml',
    ],
    'demo': [],
    'test': [],
    'license':'OPL-1',
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/4eCla2v9vD8',
    "images":['static/description/Banner.gif'],
}