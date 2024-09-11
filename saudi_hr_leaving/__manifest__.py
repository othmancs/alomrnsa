# -*- coding: utf-8 -*-
# Part of odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "HR Leaving",
    "summary": """ HR Leaving """,
    "description": """
        HR Leaving
    """,
    "author": "Synconics Technologies Pvt. Ltd.",
    "website": "http://www.synconics.com",
    "category": "Generic Modules/Human Resources",
    "version": "1.0",
    "license": "OPL-1",
    "depends": ["sync_hr_payroll_account", "saudi_hr"],
    "data": [
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        "data/leaving_email_template_data.xml",
        "data/hr_leaving_data.xml",
        "views/saudi_hr_employee_leaving_view.xml",
    ],
    "demo": ["demo/demo.xml"],
    "images": ["static/description/main_screen.png"],
    "price": 0.0,
    "currency": "EUR",
    "installable": True,
    "application": True,
    "auto_install": False,
}
