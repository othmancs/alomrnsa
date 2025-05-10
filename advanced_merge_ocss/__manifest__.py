{
    'name': 'Advanced Merge Tools',
    'version': '16.0.1.0',
    'summary': 'دمج غير محدود للسجلات مع تجاوز القيود',
    'description': 'يسمح بدمج أي عدد من السجلات (مثل جهات الاتصال) مع تحكم كامل في الحقول المدمجة.',
    'author': 'OTHMANCS',
    'depends': ['base', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/merge_views.xml',
        'views/partner_views.xml',
        'wizard/wizard_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}