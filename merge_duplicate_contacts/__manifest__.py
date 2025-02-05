{
    'name': 'Merge Duplicate Contacts',
    'version': '16.0.1.0.0',
    'category': 'Contacts',
    'summary': 'Merge contacts with similar names or tax IDs.',
    'author': 'Othmancs92',
    'depends': ['base', 'contacts'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
}
