# -*- coding: utf-8 -*-
{
    'name': "تخصيص تكاليف الأراضي مع إضافة تكاليف العمران",
    'summary': """
        إضافة خيار تكاليف العمران في تكاليف الأراضي وتخصيص آلية الحساب""",
    'description': """
        هذا الموديول يضيف خيار "تكاليف العمران" في نموذج stock.landed.cost
        ويقوم بحساب التكاليف حسب النسبة المئوية للقيمة الإجمالية
    """,
    'author': "OTHMANCS",
    'website': "http://www.yourcompany.com",
    'category': 'Inventory',
    'version': '16.0.1.0.0',
    'depends': ['stock_landed_costs'],
    'data': [
        'views/landed_cost_views.xml',
    ],
    'license': 'LGPL-3',
}