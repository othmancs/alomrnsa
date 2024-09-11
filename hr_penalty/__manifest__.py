# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    "name": "HR Penalty",
    "summary": "HR Penalty",
    "description": """
        Give Penalty to the employee based on panelty type.
        """,
    "author": "Synconics Technologies Pvt. Ltd.",
    "website": "http://www.synconics.com",
    "category": "HR",
    "version": "1.0",
    "license": "OPL-1",
    "depends": ["hr_contract", "account", "hr_warning", "saudi_hr_eos"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/penalty.xml",
        "data/hr_payroll_data.xml",
        "views/hr_penalty_name.xml",
        "views/hr_punishment.xml",
        "views/hr_penalty.xml",
        "views/hr_penalty_register.xml",
        "views/hr_employee.xml",
        "views/hr_warning.xml",
        "views/hr_payslip.xml",
    ],
    "installable": True,
    "auto_install": False,
}
