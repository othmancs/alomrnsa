# -*- coding: utf-8 -*-

{
    "name": "HR Employee Self Service",
    "version": "16.0.0.1",
    "category" : "Human Resources",
    "license": "Other proprietary",
    "summary": """This module allow your employee to have HR self service in Odoo.""",
    "description": """
Employee to manage Timesheet
Employee to manage Detail Activities
Employee to mofy attendes
Employee to manage own leave request
Employee to manage Expenses
Employee to send maintanance requests
Employee to manage contracts
Employee to manage projects
Employee to manage Tasks
""",
    "author": "Musa Abdullah",
    "website": "https://www.linkedin.com/in/musa-abdullah-odoo/",
    "support": "musaabdalwahed@gmail.com",
    "images": ["static/description/img1.jpg"],
    "depends": [
                'hr_timesheet',
                'hr_contract',
                "hr_holidays",
                "hr_expense",
                "hr_attendance",
                "hr_maintenance",
                "project",
                ],
    "data":[
        # "security/ir.model.access.csv",
        "views/employee_view.xml",
        "views/menu.xml",
    ],
    "installable" : True,
    "application" : False,
    "auto_install" : False,
}

