# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Human Resource Groups Configuration",
    'summary': """ Human Resource """,
    'description': """
            Human Resource Groups Configuration
        """,
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'category': 'Human Resources/Employee',
    'version': '16.0.1.0',
    'license': 'OPL-1',
    'sequence': 20,
    'depends': ['saudi_hr_branch'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_groups_configuration_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
