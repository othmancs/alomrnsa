{
    'name': 'Customer Balance in Sales',
    'version': '16.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'Display customer balance in sales orders',
    'description': '''
Customer Balance in Sales for Odoo
================================
Key features:
- Shows customer balance in quotations
- Real-time partner ledger balance display
- Helps salespeople make informed decisions
    ''',
    'author': 'IeT | Innovation Enterprise',
    'website': 'https://www.iet.eg',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'sale_management',
        'account',
    ],
    'data': [
        'views/sale_order_views.xml',
        'report/sale_order_report_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'customer_balance_sales/static/src/css/style.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'sequence': 1,
}