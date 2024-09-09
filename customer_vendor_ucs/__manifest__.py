# -*- coding:utf-8 -*-
##############################################################################
#
#    ODOO Open Source Management Solution
#
#    ODOO Addon module by Uncanny Consulting Services LLP
#    Copyright (C) 2022 Uncanny Consulting Services LLP (<https://uncannycs.com>).
#
##############################################################################
{
    "name": "Separate Customer Vendor ",
    "summary": """Separate Customer Vendor """,
    "description": """
                    In this module fields are created for segregating customer 
                    and vendor separately in sale and purchase module.
                    """,    
    "version": "16.0.1.0.0",
    "category": "Tools",
    "author": "Uncanny Consulting Services LLP",
    "maintainers": "Uncanny Consulting Services LLP",
    "website": "https://uncannycs.com",
    "license": "Other proprietary",
    "installable": True,

    "depends": ["sale_management", "purchase"],

    "data": [
        "views/sale_order_view.xml",
        "views/res_partner_view.xml",
        "views/purchase_order_view.xml",
    ],
    
    "images": ["static/description/banner.gif"],
    
}
