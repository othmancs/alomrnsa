# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, _
from odoo.exceptions import UserError


class BeltWage(models.AbstractModel):
    _name = "report.hr_evolution.report_wage_belt"
    _description = "Wage Belt"
    # Not in Use

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
        return {
            "doc_ids": self.ids,
            "doc_model": model,
            "data": data,
            "docs": docs,
        }
