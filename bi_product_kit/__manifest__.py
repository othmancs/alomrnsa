# -- coding: utf-8 --
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Product Kit Bundle',
    'version': '16.0.0.1',
    'category': 'Sales',
    'summary': 'Combine product pack product kit product bundle product pack item on product combo product on sale bundle product delivery bundle product pack kit combine product combine product variant bundle item pack sales bundle delivery pack bundle kit products kit',
    'description' :""" This odoo app helps user to create a kit product, use existing product as a kit, add sub products with quantity and price, Calculate price from kit sub products or enter fix price, sell kit product only and create and deliver kit sub product, Also stock for kit sub products will be managed accordingly. Also customer invoice will created for kit product. Kit with sub products and quantity will also printed on sales order and customer invoice.

	Kit, kit
	Product Kit, product kit
	Product kit with sub products
    """,
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.in',
    "price": 39,
    "currency": 'EUR',
    'depends': ['base', 'sale', 'sale_management', 'product','stock', 'sale_order_line_multi_warehouse'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_view.xml',
        'report/sale_templates.xml',
        'report/invoice_templates.xml',
        
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/nw-9yJvv7Io',
    "images":['static/description/Banner.gif'],
    "license":'OPL-1',
}
