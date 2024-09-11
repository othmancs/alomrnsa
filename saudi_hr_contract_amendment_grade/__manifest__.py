# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': "HR Contract Amendment Grade",
    'summary': "HR Contract Amendment Grade",
    'description': """ Transfer Employee""",
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'category': 'HR',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['saudi_hr_contract_amendment', 'saudi_hr_grade'],
    'data': [
        'views/transfer_employee_view.xml',
    ],
    'demo': [
        # 'demo/demo.xml'
    ],
    'installable': True,
    'auto_install': False,
}
