# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Hr Recruitment Custom Visa",
    "summary": """ Hr Recruitment Custom Visa """,
    "description": """ """,
    "author": "Synconics Technologies Pvt. Ltd.",
    "website": "http://www.synconics.com",
    "category": "Human Resources",
    "version": "1.0",
    "license": "OPL-1",
    "depends": ["saudi_hr_recruitment_custom", "saudi_hr_visa_recruiter"],
    "data": [
        "views/hr_recruitment_custom_visa_view.xml",
    ],
    # only loaded in demonstration mode
    "demo": [],
    "installable": True,
    "auto_install": False,
}
