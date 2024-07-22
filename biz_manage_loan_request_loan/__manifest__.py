{
    'name': 'Bizapps - Manage Loan Request of Employees',
    'version': '16.0.1.0.0',
    'summary': 'Manage Loan Requests',
    'description': """
        Helps you to manage Loan Requests of your company's staff.
        """,
    "author": "support@bizapps.vn",
    "maintainer": "support@bizapps.vn",
    "contributors": ["support@bizapps.vn"],
    "website": "https://bizapps.vn/ung-dung",
    'category': 'Generic Modules/Human Resources',
    'company': 'Bizapps',
    'support': 'support@bizapps.vn',
    'depends': [
        'base', 'hr_payroll', 'hr', 'account','biz_hr_payslip'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_loan_seq.xml',
        'data/salary_rule_loan.xml',
        'views/hr_loan.xml',
        'views/hr_payroll.xml',
    ],
    "images": ["static/description/background.png"],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
