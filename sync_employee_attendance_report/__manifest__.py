# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Attendance Report",
    'summary': """New Module For Employee Attendance Report""",
    'description': """
        Create new Module for Employee Attendance Report
    """,
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'license': 'OPL-1',
    'category': 'HR',
    'version': '1.0',
    'depends': ['hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/employee_attendance_report_wizard.xml',
        'views/menu.xml',
        'report/employee_attendance_report.xml',
    ],
    'installable': True,
    'application': False,
}
