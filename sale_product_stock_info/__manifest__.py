# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#################################################################################
# Author      : Grow Consultancy Services (<https://www.growconsultancyservices.com/>)
# Copyright(c): 2021-Present Grow Consultancy Services
# All Rights Reserved.
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
#################################################################################
{
    # Application Information
    'name': 'Sales Product Stock(Warehouse/Location Wise) Information || Stock Management || Stock History',
    'category': 'Sales/Sales',
    'version': '16.0.1.0.0',  # Version: odoo_version.odoo_sub_version.major_improvment.minor_improvment.bug_fixing
    'license': 'OPL-1',

    # Summary Information
    # Summary: Approx 200 Char
    # Description:
    'summary': """
This app allows you to show the warehouse/location-wise stock inside the sale order line.

GCS also provides various types of solutions, such as Odoo WooCommerce Integration, Odoo Shopify Integration,
Odoo Direct Print, Odoo Amazon Connector, Odoo eBay Odoo Integration, Odoo Amazon Integration,
Odoo Magento Integration, Dropshipper EDI Integration, Dropshipping EDI Integration, Shipping Integrations,
Odoo Shipstation Integration, Odoo GLS Integration, DPD Integration, FedEx Integration, Aramex Integration,
Soundcloud Integration, Website RMA, DHL Shipping, Bol.com Integration, Google Shopping/Merchant Integration,
Marketplace Integration, Payment Gateway Integration, Dashboard Ninja, Odoo Direct Print Pro, Odoo Printnode,
Dashboard Solution, Cloud Storage Solution, MailChimp Connector, PrestaShop Connector, Inventory Report,
Power BI, Odoo Saas, Quickbook Connector, Multi Vendor Management, BigCommerce Odoo Connector,
Rest API, Email Template, Website Theme, Various Website Solutions, etc.

#1 Odoo Partner, Best Odoo Apps, Odoo App Store, Odoo Store, Odoo Module, Magento Store, Odoo Partner, 
Odoo Gold Partner, Odoo Silver Partner.
    """,
    'description': """
This app allows you to show the warehouse/location-wise stock inside the sale order line.

GCS also provides various types of solutions, such as Odoo WooCommerce Integration, Odoo Shopify Integration,
Odoo Direct Print, Odoo Amazon Connector, Odoo eBay Odoo Integration, Odoo Amazon Integration,
Odoo Magento Integration, Dropshipper EDI Integration, Dropshipping EDI Integration, Shipping Integrations,
Odoo Shipstation Integration, Odoo GLS Integration, DPD Integration, FedEx Integration, Aramex Integration,
Soundcloud Integration, Website RMA, DHL Shipping, Bol.com Integration, Google Shopping/Merchant Integration,
Marketplace Integration, Payment Gateway Integration, Dashboard Ninja, Odoo Direct Print Pro, Odoo Printnode,
Dashboard Solution, Cloud Storage Solution, MailChimp Connector, PrestaShop Connector, Inventory Report,
Power BI, Odoo Saas, Quickbook Connector, Multi Vendor Management, BigCommerce Odoo Connector,
Rest API, Email Template, Website Theme, Various Website Solutions, etc.

#1 Odoo Partner, Best Odoo Apps, Odoo App Store, Odoo Store, Odoo Module, Magento Store, Odoo Partner, 
Odoo Gold Partner, Odoo Silver Partner.
    """,

    # Author Information
    'author': 'Grow Consultancy Services',
    'maintainer': 'Grow Consultancy Services',
    'website': 'http://www.growconsultancyservices.com/',

    # Dependencies
    'depends': ['base', 'sale'],

    # Views
    'data': [
        'security/sale_security.xml',
        'view/sale_views.xml',
        'wizard/orderline_product_stock_info_views.xml',
        'security/ir.model.access.csv',
        'view/res_config_settings_views.xml',
    ],

    # Application Main Image    
    'images': ['static/description/app_profile_image.png'],

    # Technical
    'installable': True,
    'application': True,
    'auto_install': False,
    'active': False,
}
