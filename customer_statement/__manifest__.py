{
    'name': 'Customer Statement',
    'version': '1.0',
    'summary': 'Generate customer account statement',
    'category': 'Accounting',
    'author': 'Essam Al Mahi',
    'depends': ['account'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/customer_statement_views.xml',
        'wizard/customer_statement_wizard.xml',
        'reports/customer_statement_report.xml',
    ],
    'installable': True,
    'application': False,
}
