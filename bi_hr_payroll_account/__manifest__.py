# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


{
    'name': 'HR Payroll Accounting Community Edition',
    "version" : "16.0.0.2",
    'category': 'Human Resources',
    'license': 'OPL-1',
    'summary': 'Odoo HR Payroll Community Payroll Odoo13 payroll odoo14 payroll for community Odoo13 HR payroll Odoo14 HR payroll Human Resources payroll accounting odoo payslip salary slip employee payslip employee salaryslip HR payslip HR salaryslip odoo14 payslip odoo',
    'description' :"""
        
        Generic Payroll System Integrated with Accounting in odoo,
        Manage your employee payroll records in odoo,
        HR Payroll Accounting module in odoo,
        Easy to create employee payslip in odoo,
        Manage your employee payroll or payslip records in odoo,
        Generating journal entry in odoo,
        Managing Entries in Accounting Journals in odoo,
    
    """,
    "author": "BrowseInfo",
    "website" : "https://www.browseinfo.com",
    'depends': [
       'bi_hr_payroll', 'account'
    ],
    'data': ['views/hr_payroll_account_views.xml'],
    'demo': ['data/hr_payroll_account_demo.xml'],
    'test': ['../account/test/account_minimal_test.xml'],
    "auto_install": False,
    "installable": True,
    "live_test_url": 'https://youtu.be/6hS5AsCjC0M',
    "images":['static/description/Banner.gif'],

}
