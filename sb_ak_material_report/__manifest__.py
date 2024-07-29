# -*- coding: utf-8 -*-
# Part of Odoo, Aktiv Software PVT. LTD.
# See LICENSE file for full copyright & licensing details.


{
    "name": "sb_ak_material_report",
    "license": "OPL-1",
    "version": "16.0.1.0.0",
    "category": "Inventory",
    "depends": ["base","stock","ak_material_request","sb_mr_driver_shipping_letter"],
    "data": [

        "report/sb_ak_material_report.xml",

    ],

    "installable": True,
    "application": False,
    "auto_install": False,
}

