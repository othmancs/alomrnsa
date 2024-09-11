# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import _, api, models
from odoo.exceptions import UserError


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    @api.model
    def create(self, vals):
        ir_config_obj = self.env["ir.config_parameter"].sudo()
        if ir_config_obj.get_param("saudi_hr_vacations.join_work_after_vacation"):
            vacation_id = self.env["hr.vacation"].search(
                [
                    ("employee_id", "=", vals.get("employee_id")),
                    (
                        "state",
                        "not in",
                        ["join_work_after_vacation", "cancel", "draft"],
                    ),
                    "|",
                    ("date_start", "<", vals.get("date_to")),
                    ("date_to", "<", vals.get("date_to")),
                ]
            )
            if vacation_id:
                emp_id = self.env["hr.employee"].search(
                    [("id", "=", vals.get("employee_id"))]
                )
                raise UserError(
                    _(
                        "You can't able to create Payslip for this month duration of %s employee."
                        % emp_id.name
                    )
                )

        res = super(HrPayslip, self).create(vals)
        return res
