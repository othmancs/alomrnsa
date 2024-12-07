{
    'name': 'End of Service Management',
    'version': '1.0',
    'author': 'Your Name',
    'category': 'Human Resources',
    'description': 'Manage End of Service Benefits according to Saudi regulations.',
    'depends': ['hr'],
    'data': [
        'views/end_of_service_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}