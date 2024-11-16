# -*- coding: utf-8 -*-
{
    'name': 'Employee Settlement Module',
    'version': '1.0',
    'summary': 'Module for managing employee settlements in Odoo 16',
    'description': 'A custom module for handling employee final settlements, including vacation and end-of-service details.',
    'category': 'Human Resources',
    'author': 'Your Company Name',
    'depends': ['hr', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/employee_settlement_view.xml',
        'data/employee_settlement_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
