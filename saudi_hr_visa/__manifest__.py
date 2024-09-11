# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': "HR Employee Visa",
    'summary': """HR Employee Visa """,
    'description': """
        Manage all employee's visa request for any business or personal trip.
        Behalf of employee, HR department will manage visa process with Government/Visa council.
    """,
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'category': 'Generic Modules/Human Resources',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['hr_expense_payment', 'res_documents'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/gr_operation_data.xml',
        'data/mail_template.xml',
        'views/hr_visa_view.xml',
        'menuitem.xml',
        # 'report/visit_visa.xml',
        'report/embassy_visit_visa.xml',
        'report/business_visa.xml',
    ],
    'demo': [
        'demo/visa_demo.xml',
    ],
    'images': [
        'static/description/main_screen.png'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
