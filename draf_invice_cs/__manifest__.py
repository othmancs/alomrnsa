{
    'name': 'Multi Invoice Reset to Draft',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Allow users to reset multiple posted invoices to draft state',
    'description': """
        This module allows users to reset multiple posted invoices to draft state in the accounting module.
    """,
    'author': 'Your Name',
    'depends': ['account'],
    'data': [
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
}
