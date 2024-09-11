# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    "name": "Human Resource Manpower",
    "summary": """
        Human Resource Employee Manpower
    """,
    "description": """
        Manpower plans will be defined according to different departments with forecasted employees and leavers.
        In manpower plan line there is the details about employee and calculate employees based on current employee,
        leaving employees and critical roles
    """,
    "author": "Synconics Technologies Pvt. Ltd.",
    "website": "http://www.synconics.com/odoo-opensource-erp-middle-east-human-resource-hr-man-power-planning-employee-recruitment-training-process-management-solution",
    "category": "HR",
    "version": "1.0",
    "license": "OPL-1",
    "depends": [
        "hr_recruitment",
        "hr_fiscal_year",
        "saudi_hr",
        "saudi_hr_job_requisition",
    ],
    "data": [
        "security/ir_rule.xml",
        "security/ir.model.access.csv",
        "wizard/manpower_report_view.xml",
        "views/manpower_view.xml",
        "views/menu.xml",
    ],
    # only loaded in demonstration mode
    "demo": ["demo/demo.xml"],
    "images": ["static/description/main_screen.jpg"],
    "price": 0.0,
    "currency": "EUR",
    "installable": True,
    "auto_install": False,
    "application": False,
    "assets": {
        "web.assets_backend": [
            "saudi_hr_manpower/static/src/scss/progress.scss",
        ]
    },
}
