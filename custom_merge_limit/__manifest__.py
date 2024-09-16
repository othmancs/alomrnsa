{
    'name': 'Custom Merge Limit',
    'version': '1.0',
    'category': 'Custom',
    'summary': 'Allows merging more than 3 contacts at once.',
    'description': 'Increases the limit of merging contacts from 3 to a higher number.',
    'depends': ['base'],
    'data': [
        'views/res_partner_views.xml',  # تأكد من صحة مسار ملف XML
        'security/ir.model.access.csv',  # تأكد من صحة مسار ملف CSV
    ],
    'installable': True,
    'application': False,
}
