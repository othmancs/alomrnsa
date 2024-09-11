# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': "HR Annual Leaving",
    'summary': "HR Annual Leaving",
    'description': """
        """,
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'category': 'HR',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['saudi_hr_leaves_management', 'saudi_hr_payroll'],
    'data': [
        'security/ir.model.access.csv',
        #'report/leave_details_view.xml',
        'wizard/generate_annual_leaving.xml',
        'wizard/annual_leaving_report_view.xml',
        'views/annual_leaving_view.xml',
        'wizard/leave_encashment_view.xml',
        'wizard/hr_leave_report.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}

