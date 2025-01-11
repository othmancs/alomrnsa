# -*- coding: utf-8 -*-
{
    'name': 'Financial Report Module',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Custom Financial Reports',
    'description': 'Generates financial reports based on user inputs',
    'author': 'Essam Al Mahi',
    'depends': ['account', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/financial_report_wizard_view.xml',
        'report/financial_report_template.xml',
        'report/financial_report_action.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
