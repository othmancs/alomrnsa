{
    "name": "Employee Contact Auto Create",
    "version": "1.0",
    "category": "Human Resources",
    "summary": "Automatically create a contact for each employee",
    "description": "Creates a res.partner contact when an hr.employee is created",
    "depends": ["hr", "contacts"],
    "data": ["views/hr_employee_views.xml"],
    "installable": True,
    "application": False,
    "auto_install": False
}
