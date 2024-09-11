# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'HR Health information',
    'summary': """HR Health information """,
    'description': """
        Employee Health Information like Height, weight, Blood group etc.
    """,
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'category': 'HR',
    'version': '14.0.1.0',
    'license': 'OPL-1',
    'depends': ['saudi_hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_views.xml',
    ],
    'demo': ['demo/demo.xml'],
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
