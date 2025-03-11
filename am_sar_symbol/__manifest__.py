{
    'name': 'SAR Symbol Font | Saudi Currency Symbol | Riyal Saudi Icon',
    'version': '16.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Add the new Saudi Riyal (SAR) symbol to your Odoo system',
    'description': """
SAR Symbol Font for Odoo
رمز الريال السعودي اودو Odoo
=======================

This module adds the new Saudi Riyal () symbol to your Odoo system interfaces, including:

* PDF Reports
* Point of Sale Interface
* Invoices
* All system views

After installing this module, copy the symbol () and paste it in the currency symbol field 
for the Saudi Riyal (SAR) currency in: Accounting > Configuration > Accounting > Currencies.

Note: Please ensure there are no other font-family customizations in your system views and invoices 
that might conflict with this module.
    """,
    'author': 'bst-inn, Amro00743',
    "support": "amro00743@gmail.com",
    'website': 'https://www.linkedin.com/in/amro00743/',
    'license': 'LGPL-3',
    'price': 0.0,
    'currency': 'USD',
    'depends': ['base','web'],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'am_sar_symbol/static/src/css/style.css',
        ],
        'web.assets_frontend': [
            'am_sar_symbol/static/src/css/style.css',
        ],
        'web.assets_common': [
            'am_sar_symbol/static/src/css/style.css',
        ],
        'web.report_assets_common': [
            'am_sar_symbol/static/src/css/style.css',
        ],
        'web.report_assets_pdf': [
            'am_sar_symbol/static/src/css/style.css',
        ],
        'web.assets_qweb': [
            'am_sar_symbol/static/src/css/style.css',
        ],
        "point_of_sale.assets": [
            'am_sar_symbol/static/src/css/style.css',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
