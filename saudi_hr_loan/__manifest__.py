# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    "name": "Employee Loan Management",
    "summary": """Employee Loan Management""",
    "description": """
        Employee Loan Management also manage the installment of loan.
    """,
    "author": "Synconics Technologies Pvt. Ltd.",
    "website": "http://www.synconics.com",
    "category": "Generic Modules/Human Resources",
    "version": "16.0.1.0.0",
    "license": "OPL-1",
    "depends": ["sync_hr_payroll", "saudi_hr_contract"],
    "data": [
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        "data/hr_payroll_data.xml",
        "data/loan_data.xml",
        "data/cron.xml",
        "wizard/employee_loan_freeze_view.xml",
        "views/hr_loan_view.xml",
        "views/hr_skip_installment_view.xml",
        "views/hr_loan_operation_view.xml",
        "views/res_config_settings_view.xml",
    ],
    "demo": ["demo/demo.xml"],
    "images": ["static/description/main_screen.jpg"],
    "price": 0.0,
    "currency": "EUR",
    "installable": True,
    "application": True,
    "auto_install": False,
}
