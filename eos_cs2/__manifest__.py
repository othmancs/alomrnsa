{
    'name': 'EOS Report',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Generate End of Service Reports',
    'description': 'Module to generate End of Service reports for employees.',
    'author': 'Your Name',
    'depends': ['hr'],
    'data': [
        'views/eos_report_view.xml',
        'reports/eos_report_template.xml',
    ],
    'installable': True,
    'application': True,
}
