# -*- coding: utf-8 -*-
{
    'name': "Warehouse 15 for Odoo (barcode mobile app)",
    'author': "Cleverence",
    'website': "https://www.cleverence.com",
    'category': 'Inventory',
    'version': '1.1.1',
    'depends': ['stock'],
    'data': [
        'views/clv_stock_picking_view.xml',
        'views/clv_api_settings.xml'
    ],
    'images': ['static/images/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3'
}
