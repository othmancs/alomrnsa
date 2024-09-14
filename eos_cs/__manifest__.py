{
    'name': 'HR Service End Calculation',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Calculate and report end of service in Saudi Arabia',
    'author': 'Your Name',
    'website': 'http://yourwebsite.com',
    'depends': ['hr'],
    'data': [
        'views/hr_contract_views.xml',
        'reports/hr_service_end_report.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}
