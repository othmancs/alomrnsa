# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': "Human Resource Career Development",
    'summary': """Human Resource Career Development """,
    'description': """Human Resource Career Development """,
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'category': 'Human Resources',
    'version': '1.0',
    'sequence': 20,
    'license': 'OPL-1',
    'depends': ['saudi_hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_career_development_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': ['demo/demo.xml'],
    'images': [],
    'price': 0.0,
    'installable': True,
    'auto_install': False,
    'application': False,
}
