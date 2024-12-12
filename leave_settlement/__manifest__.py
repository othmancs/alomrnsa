{
    'name': 'Leave Settlement Module',
    'version': '16.0.1.0.0',
    'summary': 'Module for managing leave settlements in payroll.',
    'description': 'This module calculates and manages leave settlements for employees.',
    'author': 'Your Company',
    'website': 'http://www.yourcompany.com',
    'category': 'Payroll',
    'depends': ['hr', 'hr_contract'],
    'data': [
        'security/ir.model.access.csv',
        'views/leave_settlement_view.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
