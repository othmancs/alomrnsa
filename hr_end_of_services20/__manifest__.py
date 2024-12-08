# -*- coding: utf-8 -*-
{
    'name': "End of Services Reward",
    'version': "16.0.0.0",
    'summary': """
        calculation of end of services reward""",

    'description': """calculation of end of services reward
              """,
    'author': "Smart Do.",
    'company': "Smart Do.",
    'category': 'Human Resources',
    'depends': ['base', 'hr_payroll', 'hr', 'hr_contract', ],
    'live_test_url': 'https://youtu.be/RN2ha0Ttlo8',
    'data': [
        'security/ir.model.access.csv',
        'data/salary_rule.xml',
        'views/res_config.xml',
        'views/hr_employee_view.xml',
        'views/hr_contract_view.xml',
        'views/eos_reason.xml'
            ],
    'website': "https://smartdo-tech.com/",
    'images': ['static/description/eos.jpg'],
    'license': "LGPL-3",

    'installable': True,
    'application': True,
    'auto_install': False,
    
}