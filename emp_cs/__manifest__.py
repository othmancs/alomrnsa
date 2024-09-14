{
    'name': 'Vacation Salary Management',
    'version': '16.0.1.0.0',
    'summary': 'Manage and process vacation salary calculations',
    'description': 'This module handles the calculation and management of vacation salaries for employees.',
    'author': 'Your Company',
    'website': 'http://www.yourcompany.com',
    'category': 'Human Resources',
    'depends': ['hr', 'hr_payroll'],
    'data': [
        'views/vacation_salary_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}