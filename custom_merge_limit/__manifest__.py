# custom_merge_limit/__manifest__.py

{
    'name': 'Custom Merge Limit',
    'version': '1.0',
    'category': 'Custom',
    'summary': 'Customizes the contact merge limit.',
    'description': 'Allows merging more than 3 contacts at once.',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'models/res_partner.py',
    ],
    'installable': True,
    'application': False,
}
