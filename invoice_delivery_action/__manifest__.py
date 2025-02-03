{
    'name': 'Invoice Delivery Action',
    'version': '16.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Move action_view_delivery from Sales to Invoice',
    'author': 'Custom Dev',
    'license': 'LGPL-3',
    'depends': ['account', 'sale', 'stock'],
    'data': [
        'views/account_move_view.xml',
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'application': False,
}