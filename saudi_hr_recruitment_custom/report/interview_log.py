# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime

from odoo import _, api, models
from odoo.exceptions import UserError


class ActiveEmployee(models.AbstractModel):
    _name = "report.saudi_hr_recruitment_custom.report_interview_log"
    _description = "Interview Log"

    @api.model
    def _get_report_values(self, doc_ids, data=None):
        if (
            not data.get("id")
            or not self.env.context.get("active_model")
            or not self.env.context.get("active_id")
        ):
            raise UserError(
                _("Form content is missing, this report cannot be printed.")
            )
        model = self.env.context.get("active_model")
        docs = self.env[model].browse(self.env.context.get("active_id"))
        start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
        applicant = (
            self.env["hr.applicant"]
            .search([("create_date", "!=", False)])
            .filtered(
                lambda a: a.create_date.date() >= start_date
                and a.create_date.date() <= end_date
            )
        )

        return {
            "doc_ids": self.ids,
            "doc_model": model,
            "data": data,
            "docs": docs,
            "applicant": applicant,
        }
