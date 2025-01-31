{
    'name': 'Customer Payment Type Control',
    'version': '16.0.1.0.0',
    'summary': 'Control customer payment types and delivery orders',
    'category': 'Sales',
    'author': 'Othmancs',
    'website': 'https://www.yourwebsite.com',
    'depends': ['base', 'sale', 'account'],
    'data': [
        'views/customer_views.xml',
        'views/sale_views.xml',
    ],
    'installable': True,
    'application': False,
}
