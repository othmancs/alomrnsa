    #-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Payroll',
    'category': 'Human Resources',
    'sequence': 38,
    'license': 'OPL-1',
    'summary': 'Manage your employee payroll records',
    'description': "",
    'depends': [
        'hr_contract',
        'hr_holidays',
    ],
    'data': [
        'data/ir_module_category_data.xml',
        'security/hr_payroll_security.xml',
        'security/ir.model.access.csv',
        'wizard/hr_payroll_payslips_by_employees_views.xml',
        'views/send_payslip_mail.xml',
        'views/hr_contract_views.xml',
        'views/hr_salary_rule_views.xml',
        'views/hr_payslip_views.xml',
        'views/hr_employee_views.xml',
        'data/hr_payroll_sequence.xml',
        'views/hr_payroll_report.xml',
        'wizard/send_payslip_mail_view.xml',
        'data/hr_payroll_data.xml',
        'data/hr_payroll_data_allowance.xml',
        'wizard/hr_payroll_contribution_register_report_views.xml',
        'views/res_config_settings_views.xml',
        'views/report_contributionregister_templates.xml',
        'views/report_payslip_templates.xml',
        'views/report_payslipdetails_templates.xml',
        'data/send_payslip_template.xml',
    ],
}
