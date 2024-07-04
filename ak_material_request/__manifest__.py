# -*- coding: utf-8 -*-
# Part of Odoo, Aktiv Software PVT. LTD.
# See LICENSE file for full copyright & licensing details.


{
    "name": "Internal Material Request / Inter-Warehouse Request",
    "author": "Aktiv Software",
    "website": "http://www.aktivsoftware.com",
    "summary": """This module allows Warehouse users to create
                  Internal Material Requests.""",
    "description": """
        Title: Internal Material Request / Inter-Warehouse Request \n
        Author: Aktiv Software PVT. LTD. \n
        mail: odoo@aktivsoftware.com \n
        Copyright (C) 2015-Present Aktiv Software PVt. LTD. \n
    """,
    "license": "OPL-1",
    "version": "16.0.1.0.0",
    "category": "Inventory",
    "depends": ["stock", "mail", 'multi_branch_base'],
    "data": [
        "security/ir.model.access.csv",
        # "security/security.xml",
        "data/material_request_sequence.xml",
        "wizard/reject_reason_wizard_views.xml",
        "wizard/transit_location_wizard.xml",
        "report/material_request_view.xml",
        "views/material_request_view.xml",
        # "views/res_config_views.xml",
        # "views/res_company_views.xml",
        "views/stock_location.xml",
        "views/stock_picking.xml",
    ],
    "images": ["static/description/Internal_Material_Request_Banner-01.jpg"],
    "installable": True,
    "application": False,
    "auto_install": False,
    "currency": "USD",
    "price": 19.11,
}

