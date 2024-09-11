# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'HR Employee Advance Salary',
    'version': '14.0.1.0.1',
    'category': 'Generic Modules/Human Resources',
    'license': "OPL-1",
    'summary': 'Employee request for advance salary.',
    'description': """Workflow of Employee request for advance salary.
    """,
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'www.synconics.com',
    'depends': ['account', 'sync_hr_payroll', 'mail', 'saudi_hr_contract'],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_security.xml',
        'data/advance_salary.xml',
        'data/hr_payroll_data.xml',
        'views/hr_view.xml',
        'wizard/advance_salary_payment_view.xml',
        'views/hr_advance_salary_view.xml',
        'data/mail_template.xml',
        'views/hr_skip_installment_view.xml',
        'report/advance_salary.xml',
        'report/advance_salary_template.xml',
    ],
    'qweb': [],
    'demo': [],
    'images': [
        'static/description/main_screen.jpg',
    ],
    'price': 25.0,
    'currency': 'EUR',
    'installable': True,
    'application': False,
    'auto_install': False,
}
