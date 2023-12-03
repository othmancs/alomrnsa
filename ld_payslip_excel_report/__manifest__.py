# -*- coding: utf-8 -*-

{
    'name': 'Payslip Excel Report',
    'author': "Livedigital Technologies Private Limited",
    'website': "ldtech.in",
    'category': 'Payroll',
    'version': '16.0.0.0',
    'license': 'LGPL-3',
    'summary': 'Excel sheet for Payslip report',
    'description': """ Payslip excel report""",
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/payslip_xls_view.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
