{
    'name': 'ZATCA Batch Invoice Processing',
    'version': '1.0',
    'depends': ['account', 'base'],
    'author': 'Your Name',
    'category': 'Accounting',
    'description': 'Batch process invoices asynchronously with ZATCA.',
    'data': [
        'views/account_invoice_zatca_views.xml',
    ],
    'installable': True,
}
