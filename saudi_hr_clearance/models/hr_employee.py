# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models


class HREmployee(models.Model):
    _inherit = "hr.employee"

    clearance_count = fields.Integer("Clearance", compute="_compute_clearance_count")

    def _compute_clearance_count(self):
        self.clearance_count = self.env["hr.employee.clearance"].search_count(
            [("employee_id", "=", self.id)]
        )

    def action_view_clearance(self):
        self.ensure_one()
        clearance_ids = self.env["hr.employee.clearance"].search(
            [("employee_id", "=", self.id)]
        )
        tree_view = self.env.ref("saudi_hr_clearance.hr_employee_clearance_tree_view")
        form_view = self.env.ref("saudi_hr_clearance.hr_employee_clearance_form_view1")
        return {
            "type": "ir.actions.act_window",
            "name": _("Employee Clearance"),
            "res_model": "hr.employee.clearance",
            "view_mode": "from",
            "views": [(tree_view.id, "tree"), (form_view.id, "form")],
            "domain": [("id", "in", clearance_ids.ids)],
        }
