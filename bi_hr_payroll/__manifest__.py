# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'HR Payroll Community Edition',
    "version" : "16.0.0.2",
    'category': 'Human Resources',
    'license': 'OPL-1',
    'summary': 'Odoo HR Payroll Community Payroll Odoo13 payroll odoo14 payroll for community Odoo13 HR payroll Odoo14 HR payroll Human Resources payroll accounting odoo payslip salary slip employee payslip employee salaryslip HR payslip HR salaryslip odoo14 payslip odoo',
    'description' :"""
        
        Manage your employee payroll records in odoo,
        HR Payroll module in odoo,
        Easy to create employee payslip in odoo,
        Manage your employee payroll or payslip records in odoo,
        Generating payroll in odoo,
        Each employee should be defined with contracts with salary structure in odoo,
    
    """,
    "author": "BrowseInfo",
    "website" : "https://www.browseinfo.com",
    'depends': [
        'hr_contract',
        'hr_holidays',
    ],
    'data': [
        'security/hr_payroll_security.xml',
        'security/ir.model.access.csv',
        'wizard/hr_payroll_payslips_by_employees_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_salary_rule_views.xml',
        'views/hr_payslip_views.xml',
        'views/hr_employee_views.xml',
        'data/hr_payroll_sequence.xml',
        'views/hr_payroll_report.xml',
        'data/hr_payroll_data.xml',
        'wizard/hr_payroll_contribution_register_report_views.xml',
        'views/res_config_settings_views.xml',
        'views/report_contributionregister_templates.xml',
        'views/report_payslip_templates.xml',
        'views/report_payslipdetails_templates.xml',
    ],
    'demo': ['data/hr_payroll_demo.xml'],
    "auto_install": False,
    "installable": True,
    "live_test_url": 'https://youtu.be/XV14XB7nczA',
    "images":['static/description/Banner.gif'],

}
