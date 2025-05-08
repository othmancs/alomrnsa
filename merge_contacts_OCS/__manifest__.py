{
    'name': 'دمج جهات الاتصال',
    'version': '16.0.1.0.0',
    'summary': 'دمج سجلات جهات الاتصال بناء على الرقم الضريبي أو الاسم',
    'description': """
        يسمح هذا الموديول بدمج سجلات جهات الاتصال التي لها نفس الرقم الضريبي أو الاسم المتطابق.
    """,
    'author': 'OTHMANCS',
    'website': 'https://www.yourwebsite.com',
    'category': 'Tools',
    'depends': ['base', 'contacts'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/merge_contacts_views.xml',
        'wizards/merge_contacts_wizard.py',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}