# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "HR Evaluation",
    "summary": """ Human Resource Evaluation """,
    "description": """
        HR Evaluation
    """,
    "author": "Synconics Technologies Pvt. Ltd.",
    "website": "http://www.synconics.com",
    "category": "Human Resources/Employee",
    "version": "1.0",
    "license": "OPL-1",
    "sequence": 20,
    "depends": [
        "saudi_hr_it_operations",
        "saudi_hr_probation",
        "hr_emp_appraisal",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/belt_level_view.xml",
        "views/wage_template.xml",
        "wizard/wage_belt_view.xml",
        "wizard/annual_wage_template.xml",
        "wizard/annual_wage_view.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
    "application": True,
}
