{
    'name': 'Employee Contract (Saudi)',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Module to print employee contracts according to Saudi regulations',
    'description': """
        This module allows the management and printing of employee contracts 
        according to the labor laws in Saudi Arabia.
    """,
    'depends': ['hr', 'report'],
    'data': [
        'views/employee_contract_views.xml',
        'reports/employee_contract_report.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
