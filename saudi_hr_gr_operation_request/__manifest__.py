# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': "Operations Request",
    'summary': """Operations Request""",
    'description': """
        Manage different operation requests like family visa request changing profession lossing iqama etc.
    """,
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'category': 'Generic Modules/Human Resources',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['hr_expense_payment'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/gr_operation_data.xml',
        'views/gr_operations_view.xml',
    ],
    'demo': ['demo/gr_operation_demo.xml'],
    'images': [
        'static/description/main_screen.jpg'
    ],
    'price': 0.0,
    'currency': "EUR",
    'installable': True,
    'application': True,
    'auto_install': False,
}
