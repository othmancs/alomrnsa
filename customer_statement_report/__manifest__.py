{
    'name': 'Customer Statement Report',
    'version': '16.0.1.0.0',
    'summary': 'Generate Customer Statement Report from Sales Orders',
    'description': 'This module allows generating customer statement reports in sales orders.',
    'category': 'Sales',
    'author': 'Your Name',
    'depends': ['sale', 'account'],
    'data': [
        'views/sale_report.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
