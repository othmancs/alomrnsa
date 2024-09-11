# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    "name": "Employee Profile Information",
    "summary": """ Employee Profile Information""",
    "description": """
        Employee Profile Information About Experience, Qualification And Certification
    """,
    "author": "Synconics Technologies Pvt. Ltd.",
    "website": "http://www.synconics.com",
    "category": "Generic Modules/Human Resources",
    "version": "1.0",
    "license": "OPL-1",
    "depends": ["saudi_hr", "hr_recruitment"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/cron.xml",
        "data/mail_template.xml",
        "views/email_template_view.xml",
        "views/web_template_view.xml",
        "views/employee_view.xml",
    ],
    # only loaded in demonstration mode
    "demo": ["demo/demo.xml"],
    "images": ["static/description/main_screen.png"],
    "assets": {
        "web.assets_frontend": [
            "saudi_hr_exp_info/static/src/scss/employee_private_info.scss",
            "saudi_hr_exp_info/static/src/js/employee_private_info.js",
        ]
    },
    "price": 0.0,
    "currency": "EUR",
    "installable": True,
    "application": True,
    "auto_install": False,
}
