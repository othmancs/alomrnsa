{
    'name': 'Contract Termination with Financial Check',
    'version': '1.0',
    'category': 'Human Resources',
    'description': 'A module to handle contract termination with checks for outstanding financial liabilities.',
    'author': 'Othmancs 92',
    'website': 'https://yourwebsite.com',
    'depends': ['hr', 'account'],
    'data': [
        'views/contract_termination_views.xml',
        'views/account_advance_views.xml',
        'views/account_debt_views.xml',
    ],
    'installable': True,
    'application': True,
}
