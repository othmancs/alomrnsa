{
    'name': 'مخالصة الإجازة السنوية كراتب',
    'version': '16.0.1.0.0',
    'summary': 'إدارة مخالصات الإجازة السنوية كراتب للموظفين',
    'description': """
        هذا الموديول يسمح بتحويل رصيد الإجازة السنوية للموظفين إلى راتب نقدي
    """,
    'category': 'Human Resources',
    'author': 'Othmancs',
    'website': 'https://www.yourcompany.com',
    'depends': ['hr', 'hr_holidays', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/hr_leave_type_data.xml',
        'views/hr_employee_views.xml',
        'views/hr_leave_salary_advance_views.xml',
        'report/report_leave_salary_advance.xml',
        'report/report.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}