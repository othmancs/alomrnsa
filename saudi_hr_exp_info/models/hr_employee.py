# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models


class HREmployee(models.Model):
    _inherit = "hr.employee"

    qualification_ids = fields.One2many(
        "hr.qualification", "employee_id", "Qualifications"
    )
    experience_ids = fields.One2many(
        "hr.experience", "employee_id", "Previous Experience"
    )
    certification_ids = fields.One2many(
        "hr.certification", "employee_id", "Certifications"
    )
