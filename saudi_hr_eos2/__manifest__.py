# -*- coding: utf-8 -*-
# Part of odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "End Of Service",
    'summary': """
        End Of Service""",
    'description': """
        It calculate End of Services.
EOS will be divide in two ways
1. Termination
2. Resignation

EOS required joined date and leaving date of employee.
EOS calculated depends on Last Salary.
For EOS Calculation (as per provided Excel sheet)
EOS amount
+ Current Salary (days depends on leave date)
+ total annual Leave balance amount
+ other (for any addition)
- other (for any deduction)

    """,

    'author': 'erp-bank.',
    'website': 'http://www.erp-bank.com',
    'category': 'Human Resources',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': [
        'saudi_hr_contract',
        'hr_payroll_account',
        'saudi_hr_leaves_management',
        'saudi_hr_annual_leaving',
        'saudi_hr_loan','base',
        'portal','mail'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'data/hr_eos_data.xml',
        'views/hr_employee_eos_view.xml',
        'views/eos_method_view.xml',
        'menu.xml',
        'wizard/eos_details_view.xml',
        'register_qweb_report_eos.xml',
        'report/emp_experience_letter_maleqweb.xml',
        'report/emp_experience_letter_femaleqweb.xml',
    ],
    'demo': [
        'demo/demo.xml'
    ],
    'installable': True,
    'auto_install': False,
}
