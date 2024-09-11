# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "HR Training",
    'summary': """ Human Resource Training Management """,
    'description': """
        HR Training Management for Employees
    """,
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'category': 'Human Resources/Employee',
    'version': '1.0',
    'license': 'OPL-1',
    'sequence': 20,
    'depends': ['saudi_hr', 'website_slides'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/email_template.xml',
        'views/res_config_view.xml',
        'views/hr_training_view.xml',
        'views/hr_view.xml',
        'views/slide_channel_view.xml',
        'views/website_slides_template.xml'
    ],
    'demo': [
        # 'demo/user_demo.xml',
        # 'demo/demo.xml',
        # 'demo/group_configuration_demo.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
