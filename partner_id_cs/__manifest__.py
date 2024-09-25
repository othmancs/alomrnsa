{
    'name': 'Restrict Partner Creation in Sale Orders',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Prevent the creation of new partners in sale orders based on user permissions.',
    'depends': ['sale'],
    'data': [
        'security/sale_order_security.xml',
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
}
