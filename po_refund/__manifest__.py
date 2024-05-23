# -*- coding: utf-8 -*-
{
    'name': "PO Refund App",

    'description': """
        PO Refund App
    """,

    'author': "SBTechnology",
    'website': "https://www.sbtechnology.com",

    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'stock', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'application': True
}
