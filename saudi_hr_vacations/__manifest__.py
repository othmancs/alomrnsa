# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "HR Vacations",
    "summary": """ Human Resource Management """,
    "description": """
        Human Resource Management Vacations
    """,
    "author": "Synconics Technologies Pvt. Ltd.",
    "website": "http://www.synconics.com",
    "category": "HR",
    "version": "1.0",
    "license": "OPL-1",
    "sequence": 20,
    "depends": [
        "saudi_hr_leaves_management",
        "saudi_hr_visa",
        "sync_employee_advance_salary",
        "saudi_hr_contract",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/data.xml",
        "view/hr_contract_view.xml",
        "view/res_config_view.xml",
        "view/hr_vacations_view.xml",
        "view/hr_vacations_allocation_view.xml",
        "wizard/change_date_wizard_view.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
    "application": True,
}
