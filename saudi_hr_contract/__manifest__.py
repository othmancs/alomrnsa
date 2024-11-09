# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Human Resource contract",
    'summary': """ Employee Contract """,
    'description': """ Enhance the feature of base hr_contract module according to Human Resource. """,
    'author': "Synconics Technologies Pvt. Ltd.",
    'website': "http://www.synconics.com",
    'category': 'HR',
    'version': '16.1.0',
    'sequence': 20,
    'license': 'OPL-1',
    'depends': ['account',
                'hr_contract',
                'saudi_hr',
                'sync_hr_payroll',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'data/hr_payroll_data.xml',
        'data/contract_cron.xml',
        'data/contract_template.xml',
        'views/hr_employee_view.xml',
        'views/contract_view.xml',
    ],
    'demo': [
        'demo/demo.xml'
        ],
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
