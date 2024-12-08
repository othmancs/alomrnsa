{
    'name': 'End of Service (KSA)',
    'version': '16.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Manage End of Service for employees in KSA',
    'author': 'Your Company Name',
    'depends': ['hr', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/eos_views.xml',
    ],
    'installable': True,
    'application': True,
}
