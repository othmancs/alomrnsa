# -*- coding: utf-8 -*-
#################################################################################
# Author      : Kanak Infosystems LLP. (<http://kanakinfosystems.com/>)
# Copyright(c): 2012-Present Kanak Infosystems LLP.
# All Rights Reserved.
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <http://kanakinfosystems.com/license>
#################################################################################

{
    'name': 'Electronic Invoice | Saudi VAT Invoice | Saudi E-Invoice | Saudi Electronic Invoice',
    'version': '16.0.1.0',
    'sequence': 1,
    'category': 'Accounting',
    'summary': 'Saudi Electronic Invoice',
    'description': """
     Electronic Invoice- Invoice | Saudi Electronic Invoice
     Using this module you can print Saudi electronic invoice for Invoice VAT.
     According to Saudi Government QR code with Display Saudi Tax details, Supplier Name, Supplier VAT, Customer Name, Customer VAT, Invoice Date, Create Datetime, Total of VAT, Total of Amount.
     """,
    'author': 'Kanak Infosystems LLP.',
    'website': 'https://www.kanakinfosystems.com',
    'license': 'OPL-1',
    'depends': ['account'],
    'data': [
        'report/vat_invoice_report_print.xml',
        'report/vat_report_action_call.xml',
        'report/invoice_default_attach.xml',
        'report/simpli_vat_invoice_report.xml',
        'views/account_move_report_action.xml',
        'views/res_company_view.xml',
    ],
    'assets': {
        'web.assets_common': [
            'saudi_einvoice_knk/static/src/css/style.css',
        ],
    },
    'images': ['static/description/banner.gif'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
