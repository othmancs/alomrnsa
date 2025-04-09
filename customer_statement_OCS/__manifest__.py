# -*- coding: utf-8 -*-

{
    'name': "تقرير كشف حساب العميل",
    'version': '16.0.1.0.0',
    'summary': """
        تقرير مفصل بكشف حساب العميل يشمل الرصيد الافتتاحي، الحركات المالية، والرصيد الختامي
    """,
    'description': """
        تقرير كشف حساب العميل:
        - بيانات العميل الأساسية
        - الرصيد الافتتاحي
        - تفاصيل الحركات المالية (فواتير، دفعات، إشعارات)
        - الرصيد الختامي
        - تصدير إلى PDF و Excel
    """,
    'author': "Othmancs",
    'website': "https://www.example.com",
    'category': 'Accounting/Accounting',
    'depends': ['base', 'account', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/customer_statement_views.xml',
        'report/customer_statement_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'customer_statement_OCS/static/src/js/customer_statement.js',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
