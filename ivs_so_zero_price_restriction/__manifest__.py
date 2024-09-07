# -*- coding: utf-8 -*-
{
    'name': "Prevent Sales Orders with Zero Unit Price",
    'summary': "Prevent users from confirming sales orders if a line has a Unit Price equal to Zero",
    'description': "Prevent Sales Orders with Zero Unit Price",
    'author': 'I Value Solutions',
    'website': 'www.ivalue-s.com',
    'email': 'info@ivalue-s.com',
    'license': 'OPL-1',
    'category': 'Sales',
    'version': '0.1',
    'images': ['static/description/banner.png'],
    'depends': ['base', 'sale_management'],
    'data': [
        # 'security/ir.model.access.csv',
        'security/security.xml',
        'views/views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
