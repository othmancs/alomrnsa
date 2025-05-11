# -*- coding: utf-8 -*-

{
    'name': "Merge Partners by VAT",
    'summary': """
        Merge duplicate partners based on VAT number""",
    'description': """
        This module allows you to merge duplicate partners in Odoo based on their VAT number,
        keeping all related transactions and documents.
    """,
    'author': "OTHMANCS",
    'website': "http://www.yourwebsite.com",
    'category': 'Tools',
    'version': '16.0.1.0.0',
    'depends': ['base', 'contacts'],
    'data': [
        'views/partner_view.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}