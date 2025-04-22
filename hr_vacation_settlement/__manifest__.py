{
    'name': 'تصفية الإجازة السنوية',
    'version': '16.0.1.0.0',
    'summary': 'إدارة تصفية الإجازة السنوية للموظفين',
    'description': """
        هذا الموديول يقوم بحساب تصفية الإجازة السنوية للموظفين حسب نظام العمل السعودي
        ويتضمن خصم سلف الإجازة من المبلغ المستحق.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'category': 'Human Resources',
    'depends': ['hr', 'hr_holidays', 'mail'],
    'data': [
        # 'security/ir.model.access.csv',
        'data/hr_vacation_settlement_data.xml',
        'views/hr_vacation_settlement_views.xml',
        'report/vacation_settlement_report.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}