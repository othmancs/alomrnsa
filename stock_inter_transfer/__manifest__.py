# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': "Inter Warehouse Transfer",
    'version': '1.0',
    'category': 'EWS',
    'summary': 'Inter Warehouse Transfer',
    'description': """
    Transfer stock from one warehouse to another warehouse
Warehouse Transfer
Stock Transfer
Stock
Transfer
    """,
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'depends': ['stock'],
    'data': [
        "data/ir_sequence.xml",
        "security/ir.model.access.csv",
        "views/stock_transfer_view.xml",
        "views/stock_picking_view.xml",
        "views/res_config_settings_view.xml"
    ],
    'images': ['static/description/main_screen.png'],
    'price': 70.0,
    'currency': 'EUR',
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
}
