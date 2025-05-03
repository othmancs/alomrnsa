# -*- coding: utf-8 -*-
{
    'name': "تقرير طلبات النقل بين الفروع",
    'summary': """
        تقرير مفصل لطلبات النقل بين الفروع مع مقارنة الكميات المرسلة والمستلمة
    """,
    'description': """
        هذا الموديول يقوم بإنشاء تقارير لطلبات النقل بين الفروع ويظهر:
        - الكمية المطلوبة
        - الكمية المتاحة في الفرع المصدر
        - الكمية المرسلة
        - الكمية المستقبلة
        - الفرق بين المرسلة والمستلمة
    """,
    'author': "OTHMANCS",
    'website': "http://www.yourcompany.com",
    'category': 'Inventory',
    'version': '15.0.1.0.0',
    'depends': ['base', 'stock', 'ak_material_request'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/material_transfer_report_views.xml',
        'wizard/material_transfer_report_wizard_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
