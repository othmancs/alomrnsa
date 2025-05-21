{
    'name': 'تصفير أرصدة الإغلاق',
    'version': '16.0.1.0.0',
    'summary': 'تصفير أرصدة الإغلاق لجميع الحسابات بتاريخ معين',
    'description': """
        هذا الموديول يسمح بإنشاء قيود محاسبية لتصفير أرصدة الإغلاق
        لجميع الحسابات بتاريخ محدد.
    """,
    'author': 'Othmancs',
    'website': 'https://www.yourwebsite.com',
    'depends': ['account'],
    'data': [
        'views/account_balance_zero_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
