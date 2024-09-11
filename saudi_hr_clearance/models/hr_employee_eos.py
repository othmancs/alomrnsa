# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models
from odoo.exceptions import UserError


class HrEmployeeEos(models.Model):
    _inherit = "hr.employee.eos"

    def _compute_clearance_mandatory_for_eos(self):
        clearance_mandatory_for_eos = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("saudi_hr_eos.clearance_mandatory_for_eos")
        )
        for record in self:
            record.clearance_mandatory_for_eos = clearance_mandatory_for_eos

    clearance_mandatory_for_eos = fields.Boolean(
        "Clearance Mandatory for EOS",
        copy=False,
        compute="_compute_clearance_mandatory_for_eos",
        default=lambda self: self.env["ir.config_parameter"]
        .sudo()
        .get_param("saudi_hr_eos.clearance_mandatory_for_eos"),
    )

    def check_clearance(self):
        self.ensure_one()
        if self.clearance_mandatory_for_eos:
            clearance_id = self.env["hr.employee.clearance"].search(
                [
                    ("employee_id", "=", self.employee_id.id),
                ],
                limit=1,
            )
            if not clearance_id:
                raise UserError(
                    _(
                        "There is a no clearance for this employee please create clearance first."
                    )
                )

    def eos_confirm(self):
        self.check_clearance()
        return super(HrEmployeeEos, self).eos_confirm()

    def calc_eos(self):
        self.check_clearance()
        return super(HrEmployeeEos, self).calc_eos()

    def create_clearance(self):
        """Create Clearance Object."""
        self.ensure_one()
        clearance_id = self.env["hr.employee.clearance"].create(
            {
                "employee_id": self.employee_id.id,
                "seniority_date": self.date_of_leave,
                "company_id": self.company_id and self.company_id.id,
            }
        )
        clearance_id.clearance_confirm()
        return True
