# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Website Product Name',
    'category': 'Website',
    'website': 'https://www.pptssolutions.com/',
    'author': 'PPTS India Pvt Ltd',
    'summary': 'Website Product Name',
    'version': '16.0',
    'license': 'LGPL-3',
    'description': """
    Website Product Name
        """,
    'depends': ['website_sale', 'product'],
    'data': [
        'views/website_template.xml',
        'views/product_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
}
