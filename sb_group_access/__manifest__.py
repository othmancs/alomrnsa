# -*- coding: utf-8 -*-
{
    'name': "SB Group Access",

    'description': """
        sb_group_access
    """,

    'author': "SBTechnology",
    'website': "https://www.sbtechnology.com",

    'category': 'sale',
    'version': '0.1',

    'depends': ['base', 'sale'],

    'data': [
        'security/sb_sale_group_access.xml',
        'security/sb_product_group_access.xml',
        'views/sale_order.xml',
    ],
    'application': True
}
