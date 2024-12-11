# -*- coding: utf-8 -*-
{
    'name': "HR Loans",

    'summary': """
        Loan Requests to employees""",

    'description': """
        Loan Requests to employees
    """,

    'author': "Crevisoft Corporate",
    'website': "https://www.crevisoft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mail', 'hr', 'hr_payroll', 'hr_payroll_account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_loan_seq.xml',
        'data/salary_rule_loan.xml',
        'views/hr_loan.xml',
        'views/hr_payroll.xml',
        # 'views/res_config_views.xml',
    ]
}
