# -*- coding: utf-8 -*-

{
    'name': 'Sb.Purchase.Order',
    'version': '16.0.1.0.0',
    'summary': 'Extension to copy partner_ref from purchase order to stock picking',
    'author': 'SB',
    'depends': ['purchase', 'stock'],
    'data': [
        'views/stock_picking.xml',
    ],
    'installable': True,
    'application': False,
}
