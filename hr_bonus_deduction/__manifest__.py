# -*- coding: utf-8 -*-
{
    'name': "Bonus and Deduction",

    'summary': """
        Bonus and Deduction to employees""",

    'description': """
        Add a bonus and deduction to employees in the payslip
    """,

    
    'author': "Crevisoft Corporate",
    'website': "https://www.crevisoft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_payroll'],

    # always loaded
    'data': [
        'data/data.xml',
        'data/ir_sequence.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/hr_bonus_views.xml',
        'views/hr_deduction_views.xml',
        'views/res_config_views.xml',
        'views/hr_bonus_deduction_menu.xml',
    ]
}
