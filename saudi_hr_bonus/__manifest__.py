# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Employee Bonus",
    'summary': """ Employee Bonus Calculation """,
    'description': """
        Bonus is compensation given to an employee in addition to his/her normal wage.
        A bonus can be used as a reward for achieving specific goals set by the company,
        or for dedication to the company - or even to join the company.""",
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'category': 'HR',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['sync_hr_payroll', 'hr_fiscal_year', 'saudi_hr', 'hr_warning'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'report/report.xml',
        'data/hr_payroll_data.xml',
        'data/mail_template_data.xml',
        'data/cron.xml',
        'views/bonus_view.xml',
        'views/res_company_view.xml',
        'report/report_employee_promotion.xml',
        'report/report_employee_no_promotion.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml'
    ],
    'images': [
        'static/description/main_screen.png'
    ],
    'price': 0.0,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
}
