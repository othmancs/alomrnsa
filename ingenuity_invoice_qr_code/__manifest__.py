# -*- coding: utf-8 -*-
#############################################################################
#
#    Ingenuity Info
#
#    Copyright (C) 2023-TODAY Ingenuity Info(<https://ingenuityinfo.in>)
#    Author: Ingenuity Info(<https://ingenuityinfo.in>)
#
#
#############################################################################
{
    'name': "QR Code on Invoice",
    'author': "Ingenuity Info",
    'category': 'Other',
    'summary': """ This Module will allow to Generate QR Code for Invoice. """,
    'website': "https://ingenuityinfo.in",
    'company': 'Ingenuity Info',
    'maintainer': 'Ingenuity Info',
    'version': '16.0.0.0',
    'price': 0.0,
    'currency': 'EUR',
    'description': """ By using this module you can Generate QR Code for Invoice. Thae QR code will visible on Invoice form. 
        You can also print the QR code on Invoice as well.
    """,
    'depends': [
        'web',
        'account'
    ],
    'data': [
        'report/account_invoice_report_template.xml',
        'views/qr_code_invoice_view.xml',
    ],
    'qweb': [
        ],
    "assets": {
        "web.assets_backend": [
        ],
        "web.assets_tests": [
        ],
    },
    "images": ['static/description/Banner.gif'],
    "license": "AGPL-3",
    'installable': True,
    'application': True,
    'auto_install': False,
}