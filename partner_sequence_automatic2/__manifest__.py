# -*- coding: utf-8 -*-
# module template
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Partner Sequence',
    'version': '16.0',
    'category': 'Base',
    'license': 'AGPL-3',
    'author': "Odoo Tips",
    'website': 'https://www.facebook.com/OdooTips/',
    'depends': ['base',
                ],

    'images': ['images/main_screenshot.png'],
    'data': [
             'data/res_partner_sequence.xml',
             ],
    'installable': True,
    'application': True,
}
