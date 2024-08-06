{
    "name": "Sale Global Discount",

    'version': "16.0",

    'category': "Sales",

    "summary": "Sale Global Discount",

    'author': "INKERP",

    'website': "https://www.INKERP.com",

    "depends": ["sale", "account", "sale_management"],

    "data": ["views/sale_order_view.xml",
             "views/sale_report_templates.xml",
             "views/account_move_view.xml",
             "views/report_invoice.xml",
             ],

    'images': ['static/description/banner.png'],
    'license': "OPL-1",
    'installable': True,
    'application': True,
    'auto_install': False,

}
