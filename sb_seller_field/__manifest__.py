# -*- coding: utf-8 -*-

{
    "name": "SB Seller Field",
    "version": "1.0.0.16",
    "depends": [
        'base', 'sale', 'multi_branch_base','stock','ak_material_request'
    ],
    "data": [
        'views/material_request.xml',
        'views/stock_inventory.xml',
        'views/stock_picking.xml',
        'views/sale_order.xml',

    ],
    "installable": True,
    "auto_install": False,
}
