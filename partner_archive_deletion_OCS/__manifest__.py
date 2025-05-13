{
    'name': 'Archive Partner Deletion',
    'version': '16.0.1.0.0',
    'summary': 'Allow deletion of archived partners even with accounting entries',
    'description': """
        This module allows deletion of archived partners even if they have accounting entries,
        while preventing deletion of active partners with accounting entries.
    """,
    'author': 'OTHMANCS',
    'website': 'https://www.yourwebsite.com',
    'category': 'Tools',
    'depends': ['base', 'account'],
    'data': [
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}