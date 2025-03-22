{
    'name': 'Custom HR Contract Fix',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Fix issues related to hr.contract model',
    'depends': ['hr', 'base'],
    'data': [
        'views/hr_contract_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
