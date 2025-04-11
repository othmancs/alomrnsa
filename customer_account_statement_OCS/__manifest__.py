{
    'name': 'Customer Statement Report',
    'version': '16.0.1.0.0',
    'summary': 'Generate detailed customer account statements',
    'description': """
        This module provides detailed customer account statements
        with transaction history and balances.
    """,
    'category': 'Accounting',
    'author': 'Othmancs',
    'website': 'https://www.yourwebsite.com',
    'depends': ['account'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/customer_statement_views.xml',
        'reports/customer_statement_report.xml',
        'views/report_template.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}