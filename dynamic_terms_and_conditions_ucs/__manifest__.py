# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO Open Source Management Solution
#
#    ODOO Addon module by Uncanny Consulting Services LLP
#    Copyright (C) 2022 Uncanny Consulting Services LLP (<https://uncannycs.com>).
#
##############################################################################
{
    "name": "Dynamic Terms And Conditions",
    "summary": """Dynamic Terms And Conditions""",
    "version": "16.0.1.0.0",
    "category": "Productivity",
    "author": "Uncanny Consulting Services LLP",
    "maintainers": "Uncanny Consulting Services LLP",
    "website": "https://uncannycs.com",
    "license": "Other proprietary",
    "installable": True,
    "depends": ["sale_management", "account", "purchase", "contacts"],
    "data": [
        "views/res_company.xml",
        "views/res_config.xml",
        "views/res_country.xml",
        "report/sale_report.xml",
        "report/purchase_report.xml",
        "report/invoice_report.xml",
    ],
    "images": ["static/description/banner.gif"],
}
