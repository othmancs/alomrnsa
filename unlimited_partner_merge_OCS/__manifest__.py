{
    'name': "Unlimited Partner Merge",
    'version': '16.0.1.0.0',
    'summary': 'Allows merging unlimited contacts in Odoo',
    'description': 'Remove the 3-contact limit when merging partners in Odoo.',
    'author': 'OTHMANCS',
    'website': 'https://yourwebsite.com',
    'category': 'Tools',
    'depends': ['base'],
    'data': [
        'views/partner_merge_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}