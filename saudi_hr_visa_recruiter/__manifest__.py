# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': "Employee Visa Recruiter",
    'summary': """ Employee Visa Recruiter """,
    'description': """
        Employee visa recruiter request and Expense calculation
        Manager can put the visa request, HR Officer approve it and Expense Manager calculate the expense.
    """,
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'category': 'Generic Modules/Human Resources',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['hr_expense_payment', 'hr_recruitment'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/gr_operation_data.xml',
        'data/mail_template.xml',
        'views/hr_employee_rec_visa_view.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/recruiter_visa_demo.xml',
    ],
    'images': [
        'static/description/main_screen.png'
    ],
    "price": 0.0,
    "currency": "EUR",
    'installable': True,
    'auto_install': False,
}
