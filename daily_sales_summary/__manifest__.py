{
    'name': 'ملخص المبيعات اليومية',
    'version': '16.0.1.0.0',
    'summary': 'نموذج لتقرير ملخص حركة المبيعات اليومية',
    'description': """
        تقرير يومي يعرض ملخص حركة المبيعات يشمل:
        - المبيعات النقدية والآجلة
        - المرتجعات النقدية والآجلة
        - صناديق المبيعات
        - إجماليات المبيعات والمرتجعات
    """,
    'author': 'Othmancs',
    'website': 'https://www.yourwebsite.com',
    'category': 'Sales/Sales',
    'depends': ['account', 'sale'],
    'data': [
        'views/daily_sales_summary_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}