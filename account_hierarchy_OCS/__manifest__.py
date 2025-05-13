{
    'name': 'توسيع مستويات شجرة الحسابات',
    'version': '16.0.1.0.0',
    'summary': 'يسمح بزيادة مستويات شجرة الحسابات حسب الرغبة',
    'description': """
        هذا الموديول يسمح بإضافة مستويات إضافية لشجرة الحسابات حسب احتياجات الشركة
    """,
    'author': 'OTHMANCS',
    'website': 'https://www.yourwebsite.com',
    'category': 'Accounting/Accounting',
    'depends': ['account'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}