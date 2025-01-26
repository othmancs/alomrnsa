# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': "Customer Credit Limit With Approval",
    'version': '1.0',
    'summary': """ Configure Credit Limit for Customers and approve from sales and account manager""",
    'description': """ Activate and configure credit limit customer wise. If credit limit configured
    the system will warn or block the confirmation of a sales order if the existing due amount is greater
    than the configured warning or blocking credit limit. """,
    'author': "TechUltra Solutions Private Limited",
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'category': 'Sales',
    'depends': ['sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'data/credit_limit_approval_mail.xml',
        'wizard/warning_wizard.xml',
        'views/res_partner.xml',
        'views/sale_order.xml',
    ],
    'images': [
        'static/description/main_screen.gif',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
}
