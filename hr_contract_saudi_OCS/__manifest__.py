{
    'name': "Saudi HR Contract",
    'summary': """
        طباعة العقد الوظيفي السعودي وفق نظام العمل""",
    'description': """
        موديول لطباعة العقود الوظيفية وفق متطلبات وزارة الموارد البشرية والتنمية الاجتماعية السعودية
    """,
    'author': "Othmancs",
    'website': "http://www.yourcompany.com",
    'category': 'Human Resources',
    'version': '16.0.1.0.0',
    'depends': ['hr_contract'],
    'data': [
        'views/hr_contract_views.xml',
        'reports/employee_contract_report.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}