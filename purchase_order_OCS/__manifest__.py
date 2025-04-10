# -*- coding: utf-8 -*-

{
    'name': "تقرير أمر الشراء المخصص",
    'version': '16.0.1.0.0',
    'summary': "تقرير مخصص لأوامر الشراء مع تفاصيل كاملة",
    'description': """
        تقرير مفصل لأوامر الشراء يحتوي على:
        - معلومات الشركة والشعار
        - تفاصيل أمر الشراء
        - قائمة الأصناف مع الكميات والأسعار
        - الإجماليات النهائية
    """,
    'author': "Othmancs",
    'company': "Alomran",
    'website': "https://www.yourcompany.com",
    'category': 'Purchases',
    'depends': ['purchase', 'account'],
    'data': [
        'reports/purchase_order_report.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'purchase_order_report/static/src/css/report_styles.css',
        ],
    },
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}