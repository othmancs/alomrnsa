# -*- coding: utf-8 -*-
{
 'name': "Employee Contract Allowances/Deductions ",
 'summary': """
       Multiple Allowances/Deductions for employee""",
 'description': """
            Add many allowances/deductions to any employee, include in payroll and END of Service Reward calculation
    """,
    'author': 'Awais ali',
    'website': "https://www.upwork.com/freelancers/~018ff6830780ff04b4",
 'license': "LGPL-3",
 'category': 'HR',
 'version': '16',
 'images': ['static/description/Banner.png'],
 'depends': ['base', 'mail', 'hr_contract', 'hr_payroll'],
 'data': [
    'data/data.xml',
    'data/contract_deduction_seq.xml',
    'data/contract_allowance_seq.xml',
    'security/ir.model.access.csv',
    'security/security.xml',
    'wizard/forward_next_month.xml',
    'wizard/cash_payment_register.xml',
    'views/hr_allowance_views.xml',
    'views/hr_deduction_views.xml',
    'views/hr_contract_views.xml',
    'views/contract_deduction.xml',
    'views/contract_allowance.xml',
    'views/deduction_payslip_view.xml',
    'views/hr_employee.xml',
 ],
 'demo': []
 }
