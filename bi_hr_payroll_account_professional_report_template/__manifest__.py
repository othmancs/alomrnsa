# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
	"name":"Professional Payslip Report Template",
	"version":"16.0.0.0",
	"category":"Human Resources",
	"summary":"HR Payroll Professional Report Template for Employee Payslip Multi Report Template Fancy Report Template for Payslip Classic PDF Report Template Multiple Payslip Report Templates for Sale Purchase Invoice Odoo Standard PDF Report Template HR Payslip",
	"description":"""
        
        Professional Payslip Report Template Odoo App helps users to Customizable Report Template for Employee Payslip. We are provide various Professional Report Templates like A Odoo Standard PDF Report Template, Modern PDF Report Template, Fancy PDF Report Template, Classic PDF Report Template.
	
    """,
    "author": "BrowseInfo",
    "website" : "https://www.browseinfo.com",
    "depends":["base",
               "bi_hr_payroll_account",
               "bi_hr_payroll",
              ],
	"data":[
            "views/res_company.xml",
            "report/hr_payroll_account_professional_report.xml",
            "report/hr_payroll_account_professional_report_fency.xml",
            "report/hr_payroll_account_professional_report_classic.xml",
            "report/hr_payroll_account_professional_report_modern.xml",
            "report/hr_payroll_account_professional_report_odoo_standard.xml",
            "report/hr_payroll_details_account_professional_report_fency.xml",
            "report/hr_payroll_details_account_professional_report_classic.xml",
            "report/hr_payroll_details_account_professional_report_modern.xml",
            "report/hr_payroll_details_professional_report_odoo_standard.xml",
           ],
    'license':'OPL-1',
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/ieusOUHgIVc',
    "images":['static/description/Professional-Payslip-Report-Template-Banner.gif'],
}
