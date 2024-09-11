# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    "name": "HR Timesheet Sheet",
    "summary": "HR Timesheet Sheet",
    "description": """
        HR Timesheet Sheet
    """,
    "author": "Synconics Technologies Pvt. Ltd.",
    "website": "http://www.synconics.com",
    "category": "HR",
    "version": "1.0",
    "license": "OPL-1",
    "depends": [
        "saudi_hr_overtime",
        "sync_hr_payroll",
        "saudi_hr_leaves_management",
        "project",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/hr_payroll_data.xml",
        "views/hr_payroll_view.xml",
    ],
    "demo": [],
    "images": ["static/description/main_screen.jpg"],
    "price": 30.0,
    "currency": "EUR",
    "installable": True,
    "auto_install": False,
}
