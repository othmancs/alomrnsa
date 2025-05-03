{
    'name': 'إدارة الكميات الصحيحة للمنتجات',
    'version': '16.0.1.0.0',
    'summary': 'يمنع إدخال كسور عشرية في الكميات عندما تكون الوحدة "حبة"',
    'description': """
        هذا الموديول يضمن أن كميات المنتجات في المبيعات والمشتريات تكون أعدادًا صحيحة فقط
        عندما تكون وحدة القياس "حبة".
    """,
    'author': 'OTHMANCS',
    'website': 'https://www.yourwebsite.com',
    'category': 'Inventory',
    'depends': ['product', 'stock', 'sale', 'purchase'],
    'data': [
        'views/product_views.xml',
        'views/stock_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}