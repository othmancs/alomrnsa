# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    "name": "Human Resource Recruitment Custom",
    "summary": """
        Human Resource Recruitment Custom""",
    "description": """
        Human Resource Recruitment
    """,
    "author": "Synconics Technologies Pvt. Ltd.",
    "website": "http://www.synconics.com",
    "category": "Human Resources",
    "version": "1.0",
    "sequence": 20,
    "license": "OPL-1",
    "depends": [
        "hr_recruitment",
        "saudi_hr_job_requisition",
        "survey",
        "res_documents",
        "website_hr_recruitment",
        "hr_recruitment_survey",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/hr_recruitment_data.xml",
        "report/confirm_certificate_report_qweb.xml",
        "wizard/interview_log_report.xml",
        "wizard/interview_log.xml",
        "views/hr_recruitment_custom_view.xml",
        "views/register_qweb_report.xml",
        "views/hr_employee_view.xml",
        "views/menu.xml",
    ],
    # only loaded in demonstration mode
    "demo": [],
    "installable": True,
    "auto_install": False,
    "application": False,
}
