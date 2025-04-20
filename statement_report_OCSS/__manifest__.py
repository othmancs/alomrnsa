# -*- coding: utf-8 -*-

{
    'name': "كشف حساب العميل",
    'version': '16.0.1.0.0',
    'summary': """تقرير كشف حساب العميل مع الرصيد الافتتاحي والختامي""",
    'description': """
        تقرير مفصل لكشف حساب العميل مع إمكانية تصدير Excel و PDF
        يتضمن الرصيد الافتتاحي، الحركات المالية، والرصيد الختامي
    """,
    'author': "Your Company",
    'company': "Your Company",
    'website': "https://www.yourcompany.com",
    'category': 'Accounting',
    'depends': ['account', 'multi_branch_base'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/customer_account_statement_views.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
