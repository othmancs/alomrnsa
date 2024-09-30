{
    'name': 'HR Contract - End of Service Report',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Generate End of Service Clearance Reports within the HR Contract module',
    'description': """
        This module extends the HR Contract module to include an option for generating End of Service reports in Excel format.
    """,
    'depends': ['hr_contract', 'report_xlsx'],
    'data': [
        'views/end_of_service_wizard_view.xml',  # XML view for the wizard
        'reports/end_of_service_report.xml',     # XML report registration
    ],
    'installable': True,
    'application': False,
}
