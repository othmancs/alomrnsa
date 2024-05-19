# -*- coding: utf-8 -*-
{
    'name': "Alomran Customization",
    'version': '16.0.4',
    'summary': 'Alomran Customization',
    'sequence': 12,
    'description': """Alomran Customization""",
    'category': 'Accounting',
    'author': "hamdanerp",
    'maintainer': 'hamdanerp',
    'website': "https://www.hamdanerp.com",
    'license': 'AGPL-3',
    'depends': ['base', 'stock', 'product', 'sale_order_line_multi_warehouse', 'sale'],
    'data': [
        'views/product_category.xml',
        # 'views/product_template.xml',
        'views/sale_order.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
