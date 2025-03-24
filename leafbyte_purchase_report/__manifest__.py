# -*- coding: utf-8 -*-
#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#    LeafByte
#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
{
    'name': 'Purchase Report',
    'version': '16.0.0.0',
    'category': 'Purchase',
    'summary': """Purchase Report of all Purchase records.""",
    'description': """
        Module Description:
            This module will show all Purchase records made from the system.
    """,
    'author': 'LeafByte',
    'website': "",
    'company': 'LeafByte',
    'depends': ['base', 'purchase'],
    'data': [        
        'security/ir.model.access.csv',
        'views/purchase_report_view.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}