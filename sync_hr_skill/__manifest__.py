# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    "name": "Sync HR Skill",
    "summary": "HR Skill",
    "description": """
    """,
    "author": "Synconics Technologies Pvt. Ltd.",
    "website": "http://www.synconics.com",
    "version": "1.0",
    "sequence": 20,
    "category": "HR",
    "license": "OPL-1",
    "depends": ["hr_skills", "saudi_hr_recruitment_custom"],
    "data": [
        "data/hr_resume_data.xml",
        "data/cron.xml",
        "data/mail_template.xml",
        "views/email_template_view.xml",
        "views/hr_skill_view.xml",
    ],
    "assets": {
        "web.assets_qweb": [
            "sync_hr_skill/static/src/xml/resume_template.xml",
        ]
    },
    "demo": [],
    "price": 0,
    "currency": "EUR",
    "installable": True,
    "auto_install": False,
}
