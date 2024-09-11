# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'HR Overtime Request',
    'summary': 'HR Overtime Request',
    'description': """
        To complete some works on urgency basis or for any other reasons, Manager can send overtime request to specific group of employees and employee can accept / reject that request individually based on their convenience.
    """,
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'version': '1.0',
    'sequence': 20,
    'category': 'HR',
    'license': 'OPL-1',
    'depends': ['saudi_hr', 'hr_attendance'],
    'data': [
        "security/ir.model.access.csv",
        "security/security.xml",
        'data/mail_template.xml',
        "views/analytic_overtime_request_view.xml",
        "views/menu.xml",
    ],
    'demo': [
        # 'demo/overtime_request.xml'
        ],
    'price': 0,
    'currency': "EUR",
    'installable': True,
    'auto_install': False,
}
