# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name": "POS Multi Warehouse Product Quantity",
    "version": "16.0.0.1",
    "category": "Point of Sale",
    'summary': 'POS multiple warehouse point of sales multi warehouse point of sale multiple warehouse point of sale multi warehouse on pos warehouse management pos different warehouse pos product stock pos stock management pos inventory pos stock on different warehouse',
    "description": """ This odoo app helps user to manage point of sale order with multiple warehouse, User can configure multiple warehouse, user have also option to display "Available Quantity or Unreserved Quantity" and selected warehouses stock with selected stock type will displayed for products in point of sale screen. While selecting product user can enter quantity from different warehouse and picking will created from different warehouse with different quantity. User have also option to create picking in "READY" state and allow pos order even product out of stock. """,
    "author": "BrowseInfo",
    "website": "https://www.browseinfo.in",
    "price": 39,
    "currency": 'EUR',
    "depends": ['point_of_sale','sale','stock'],
    "data": [
          'views/warehouse_config_view.xml',
          'views/product_template.xml',
    ],           
    'assets': {
        'point_of_sale.assets': [
            'bi_pos_multi_warehouse/static/src/css/stock.css',
            'bi_pos_multi_warehouse/static/src/js/pos_warehouse.js',
            'bi_pos_multi_warehouse/static/src/js/models.js',
            'bi_pos_multi_warehouse/static/src/js/WarehouseStock.js',
            'bi_pos_multi_warehouse/static/src/js/ProductWidget.js',
            'bi_pos_multi_warehouse/static/src/xml/**/*',
        ],
        # 'web.assets_qweb': [
            
        # ],
    },
    'license': 'OPL-1',
    "auto_install": False,
    "installable": True,
    "live_test_url": 'https://youtu.be/wzWukm0bz9o',
    "images": ["static/description/Banner.gif"],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
