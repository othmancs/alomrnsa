{
    'name': 'Saudi End of Service Benefits (Non-Saudi)',
    'version': '1.0',
    'author': 'othmancs',
    'website': 'https://alomran.sa',
    'category': 'Human Resources',
    'summary': 'Module to calculate end-of-service benefits for non-Saudi employees in compliance with Saudi labor law.',
    'description': """
        Calculates end-of-service benefits based on Saudi labor laws, including rules for resignation, unjust termination, and service duration.
    """,
    'depends': ['hr', 'hr_payroll', 'hr_holidays'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/end_of_service_view.xml',
        'views/emp.exit.wizard.xml',
        # 'views/settings_view.xml',
        # 'reports/end_of_service_report.xml',
    ],
    'installable': True,
    'application': True,
}
