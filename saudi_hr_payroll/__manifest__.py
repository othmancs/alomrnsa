# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Human Resource Payroll",
    'summary': """ Human Resource Payroll """,
    'description': """ Human Resource Payroll """,
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'category': 'Human Resources',
    'version': '1.0',
    'license': 'OPL-1',
    'sequence': 20,
    'depends': [
        'sync_hr_payroll_account',
        #'hr_expense_payment',
        'saudi_hr_contract',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_payroll_data.xml',
        'security/ir_rule.xml',
        'views/other_hr_payslip.xml',
        'views/hr_payroll_view.xml',
        'views/hr_payslip_export_view.xml',
        'wizard/company_payslip_report_view.xml',
        'menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/hr_employee_demo.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
