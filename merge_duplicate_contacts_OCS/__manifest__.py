{
    'name': 'Merge Duplicate Contacts',
    'version': '1.0',
    'summary': 'Identify and merge duplicate contacts with a single click',
    'description': """
        Unify Your Contacts, Eliminate Duplicates!
        This module identifies and merges duplicate contacts sharing the same name, type, and email effortlessly.
    """,
    'author': 'OTHMANCS',
    'website': 'https://www.yourcompany.com',
    'category': 'Tools',
    'depends': ['base', 'contacts'],
    'data': [
        'views/res_partner_views.xml',
        'views/duplicate_contacts_views.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}