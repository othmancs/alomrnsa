{
    'name': 'تعديل تكاليف العمران على stock.landed.cost',
    'version': '16.0.1.0.0',
    'summary': 'إضافة طريقة تقسيم تكاليف العمران إلى تكاليف الأراضي',
    'description': """
        هذا الموديول يضيف خيار "تكاليف العمران" إلى طرق التقسيم في stock.landed.cost.lines
        ويحسب التكاليف بناءً على نسبة من تكلفة الشراء
    """,
    'author': 'OTHMANCS',
    'website': 'https://www.yourwebsite.com',
    'depends': ['stock_landed_costs', 'product'],
    'category': 'Inventory',
    'data': [
        'views/stock_landed_cost_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
