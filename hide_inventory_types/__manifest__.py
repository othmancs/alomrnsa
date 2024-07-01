# -*- coding: utf-8 -*-
{
    'name': "Hide Inventory Types",

    'description': """
        Hide Inventory Types
    """,

    'author': "SBTechnology",
    'website': "https://www.sbtechnology.com",

    'category': 'Inventory',
    'version': '16.0.1',
    'license': 'AGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'application': True
}
