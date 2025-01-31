{
    'name': 'Customer Type and Sale Order Behavior',
    'version': '1.0',
    'category': 'Sales',
    'author': 'Your Name',
    'website': 'https://www.example.com',
    'depends': ['base', 'sale', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/partner_view.xml',
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'application': False,
}
