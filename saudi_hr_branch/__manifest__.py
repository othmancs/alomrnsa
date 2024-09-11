# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "HR Branch",
    'summary': """Human Resource Branch option""",
    'description': """
            Human Resource Groups Configuration
        """,
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'category': 'Human Resources/Employees',
    'version': '16.0.1.0',
    'sequence': 20,
    'license': 'OPL-1',
    'depends': ['hr'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_branch_view.xml',
        'views/res_config_setting_view.xml',
        'views/menu.xml'
    ],
    'demo': [
        # 'demo/office_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
