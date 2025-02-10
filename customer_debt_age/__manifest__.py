{
    'name': 'Customer Debt Age',
    'version': '1.0',
    'summary': 'Calculate the debt age for customers based on unpaid invoices',
    'category': 'Accounting',
    'author': 'Essam Al Mahi',
    'depends': ['account'],
    'data': [
        'views/res_partner_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
