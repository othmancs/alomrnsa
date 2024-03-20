# -*- coding: utf-8 -*-
{
    'name': "SB Adjustment Custom",

    'description': """
        SB Inventory Adjustment Custom
    """,

    'author': "SBTechnology",
    'website': "https://www.sbtechnology.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'sync_inventory_adjustment'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'application': True
}
