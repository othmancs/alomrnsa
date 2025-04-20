{
    'name': 'Customer Statement Report',
    'version': '16.0.1.0.0',
    'summary': 'Generate Customer Account Statement',
    'description': """
        Generate detailed customer account statement with opening and closing balances
        Filter by date range and branch
    """,
    'category': 'Accounting',
    'author': 'Your Name',
    'website': 'https://www.yourwebsite.com',
    'license': 'AGPL-3',
    'depends': ['account', 'multi_branch_base'],
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/customer_statement_wizard.xml',
        'reports/customer_statement_report.xml',
        'reports/customer_statement_template.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}