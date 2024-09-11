# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models


class HREmployee(models.Model):
    _inherit = "hr.employee"

    jd_number = fields.Char(related="job_id.jd_number", string="JD")

    @api.onchange("coach_id")
    def onchage_coach_id(self):
        if self.coach_id:
            department = self.env["hr.department"].search(
                [
                    ("manager_id", "=", self.coach_id.id),
                    "|",
                    ("company_id", "=", False),
                    ("company_id", "=", self.company_id.id),
                ],
                limit=1,
            )
            if department:
                self.department_id = department.id


class ResUsers(models.Model):
    _inherit = "res.users"

    jd_number = fields.Char(related="employee_id.jd_number", string="JD")
    job_position_id = fields.Many2one(
        "hr.job", related="employee_id.job_id", string="Job Position"
    )
