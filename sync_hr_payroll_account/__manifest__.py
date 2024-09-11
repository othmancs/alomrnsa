#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Payroll Accounting',
    'category': 'Human Resources',
    'license': 'OPL-1',
    'sequence': 40,
    'summary': 'Generic Payroll system Integrated with Accounting.',
    'description': """
Generic Payroll system Integrated with Accounting.
==================================================

    * Expense Encoding
    * Payment Encoding
    * Company Contribution Management
    """,
    'depends': ['sync_hr_payroll', 'account'],
    'data': ['views/hr_payroll_account_views.xml'],

}
