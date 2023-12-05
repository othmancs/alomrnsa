# -*- coding: utf-8 -*-
{
'name': 'Discount on Purchase Order',
'summary': 'Configure discount percentage on the purchase order lines',
'description': '''
        
    ''',
'author': 'Openinside',
'website': 'https://www.open-inside.com',
'license': 'OPL-1',
'category': 'Purchases',
'version': '16.0.0.0.0',
'depends': ['purchase'],
'data': ['views/purchase_order_line.xml', 'views/purchase_order.xml'],
'odoo-apps': True,
'images': ['static/description/cover.png'],
'installable': True,
'post_init_hook': '_set_price_before',
'price': 0.0,
'application': False,
'currency': 'USD'
}