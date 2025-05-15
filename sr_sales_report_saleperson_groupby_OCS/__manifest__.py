# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

{
    'name': 'Sales Report By Saleperson',
    'category': 'sale',
    'version': '16.0.0.0',
    'summary': 'This module provides Sales Report By Saleperson.',
    'website':"sitaramsolutions.in",
    'author': 'Sitaram',
    "license": "OPL-1",
    'description': '''This module provides Sales Report By Saleperson.
                      With the help of this moudule you can print sales report with groupby sale person.
                      sale person groupby report.
                      sale report.
                      '''
                   ,
    'depends': ['base', 'sale_management'],
    'data':[
        'security/ir.model.access.csv',
        'reports/action_report_salesperson.xml',
        'reports/sale_report_view.xml',
        'wizards/sale_report_wizard.xml',
    ],
    'images': ['static/description/banner.png'],
    'auto_install': False,
    'installable': True,
    'application': False,
}