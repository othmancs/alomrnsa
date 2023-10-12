# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Domiup (<http://domiup.com>).
#
##############################################################################

{
    'name': 'Website Store Pickup',
    'version': '16.1.0.0',
    'category': 'Website/Website',
    'description': """Customer can pick the product at store""",
    'summary': '''Customer can pick the product at store''',
    'live_test_url': 'https://demo16.domiup.com',
    'website': '',
    'author': 'Domiup',
    'price': 50,
    'currency': 'EUR',
    'license': 'OPL-1',
    'support': 'domiup.contact@gmail.com',
    'depends': [
        'website_sale_delivery',
    ],
    'data': [
        'views/delivery_carriers_views.xml',
        'views/stock_warehouse_views.xml',
        'views/sale_order_views.xml',
        'views/website_sale_delivery_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_pick_at_store/static/src/scss/style.scss',
            'website_pick_at_store/static/src/js/website_sale_delivery.js',
            'website_pick_at_store/static/src/xml/store_list.xml',
        ],
    },
    'test': [],
    'demo': [],
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'active': False,
    'application': False,
}
