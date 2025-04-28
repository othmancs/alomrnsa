{
    'name': 'منع تصديق التحويل دون فاتورة',
    'version': '16.0.1.0.0',
    'summary': 'يمنع إنشاء تصديق التحويل في المخازن دون تأكيد إنشاء الفاتورة',
    'description': """
        هذا الموديول يمنع إنشاء تصديق التحويل في المخازن دون تأكيد إنشاء الفاتورة لنفس أمر التوصيل.
    """,
    'author': 'OTHMANCS',
    'website': 'https://www.yourwebsite.com',
    'category': 'Inventory/Inventory',
    'depends': ['stock', 'account'],
    'data': [
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}