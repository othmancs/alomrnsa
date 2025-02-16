{
    'name': 'Delete Customer Records',
    'version': '1.0',
    'summary': 'Module to delete all customer transactions and records',
    'category': 'Accounting',
    'author': 'Othmancs',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/delete_customer_view.xml',
        'wizard/delete_customer_wizard.xml',
    ],
    'installable': True,
    'application': False,
}