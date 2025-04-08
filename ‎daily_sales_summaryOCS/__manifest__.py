{
    'name': 'Daily Sales Summary',
    'version': '1.0',
    'summary': 'ملخص حركة المبيعات اليومية',
    'description': """
        تقرير يومي لحركة المبيعات والتحصيل
    """,
    'author': 'othmancs',
    'website': 'https://www.yourwebsite.com',
    'category': 'Sales',
    'depends': ['base', 'account', 'sale'],
    'data': [
        'views/daily_sales_summary_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}