# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Human Resource Overtime',
    'summary': 'Human Resource Overtime',
    'description': """
        Calculate employee overtime based on employee attendance and overtime limit.
    """,
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'category': 'HR',
    'version': '1.1',
    'license': 'OPL-1',
    'depends': ['hr_attendance', 'saudi_hr_contract'],
    'data': [
        'views/saudi_hr_overtime_view.xml',
    ],
    'demo': [
            'demo/demo.xml',
            'demo/contract_demo.xml',
            ],
    "price": 80,
    "currency": "EUR",
    'images': [
        'static/description/main_screen.jpg'
    ],
    'installable': True,
    'auto_install': False,
}
