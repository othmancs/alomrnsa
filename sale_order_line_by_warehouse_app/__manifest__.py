# -*- coding: utf-8 -*-

{
    "name" : "Sale Order Multi Warehouse App",
    "author": "Edge Technologies",
    "version" : "16.0.1.1",
    "live_test_url":'https://youtu.be/CEp6ASLFo3c',
    "images":["static/description/main_screenshot.png"],
    'summary': 'Sale order line by warehouse sale order multiple warehouse sale order multiple warehouse sale multi warehouse sales multi warehouse by sale order line warehouse by sale line wise warehouse sale order line wise warehouse on sale order line warehouse select.',
    "description": """This module helps to create delivery order according to related warehouse.""",
    "license" : "OPL-1",
    "depends" : ['base','sale_management','stock'],
    "data": [
            'views/sale_config_settings.xml',
            'views/sale_order_line_by_warehouse.xml', 
    ],
    "auto_install": False,
    "installable": True,
    "price": 12,
    "currency": 'EUR',
    "category" : "Sales",
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
