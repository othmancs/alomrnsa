# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "HR Clearance",
    "summary": """ HR Clearance """,
    "description": """HR Clearance """,
    "author": "Synconics Technologies Pvt. Ltd.",
    "website": "http://www.synconics.com",
    "category": "Human Resources",
    "version": "1.0",
    "license": "OPL-1",
    "depends": ["account", "saudi_hr_eos", "saudi_hr_loan"],
    "data": [
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        "data/employee_clearance_data.xml",
        "views/hr_employee_clearance_view.xml",
        "views/hr_employee_view.xml",
        "views/res_config_settings_view.xml",
        "views/hr_employee_eos_view.xml",
        "reports/hr_employee_clearance_report.xml",
        "views/menu.xml",
    ],
    "images": [],
    "price": 0.0,
    "demo": [
        # 'demo/demo.xml'
    ],
    "installable": True,
    "auto_install": False,
}
