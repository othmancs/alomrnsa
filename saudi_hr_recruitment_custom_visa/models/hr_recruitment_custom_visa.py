# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date, datetime

from dateutil import relativedelta
from odoo import fields, models


class HrRecruitmentCustomVisa(models.Model):
    _inherit = "hr.applicant"

    rec_visa_id = fields.Many2one(
        "hr.employee.rec.visa",
        string="Visa",
        tracking=True,
        help="Employee Visa linked to the applicant.",
        copy=False,
    )

    def processed_visa(self):
        """
        Creates a new visa record for an employee and returns a view of the created record.

        :return: Returns a dictionary with information about the views to be displayed after
        processing the visa.
        """
        visa_obj = self.env["hr.employee.rec.visa"]
        for applicant in self:
            form_view = self.env.ref(
                "saudi_hr_visa_recruiter.hr_employee_rec_visa_form"
            )
            tree_view = self.env.ref(
                "saudi_hr_visa_recruiter.hr_employee_rec_visa_tree"
            )
            new_visa_id = visa_obj.create(
                {
                    "employee_id": applicant.emp_id.id or False,
                    "email": applicant.email_from,
                    "visa_for": "individual",
                    "reason_of_visa": "new_join_employee",
                    "request_by_id": self.env.uid,
                    "nationality": applicant.country_id.id or "",
                    "requested_date_from": date.today().strftime("%Y-%m-%d"),
                    "requested_date_to": str(
                        datetime.now()
                        + relativedelta.relativedelta(months=+3, day=1, days=-1)
                    )[:10],
                }
            )
            applicant.write({"rec_visa_id": new_visa_id.id})
        return {
            "view_mode": "tree, form",
            "res_model": "hr.employee.rec.visa",
            "view_id": False,
            "views": [(form_view.id, "form"), (tree_view.id, "tree")],
            "type": "ir.actions.act_window",
            "res_id": new_visa_id.id,
            "target": "current",
            "nodestroy": True,
        }

    def action_get_created_emp_visa(self):
        """
        Return a visa form on a wizard for creating a new visa.

        :return: A dictionary containing information for displaying a form and tree view for a visa form
        on a wizard.
        """
        self.ensure_one()
        form_view = self.env.ref("saudi_hr_visa_recruiter.hr_employee_rec_visa_form")
        tree_view = self.env.ref("saudi_hr_visa_recruiter.hr_employee_rec_visa_tree")
        return {
            "view_mode": "tree, form",
            "res_model": "hr.employee.rec.visa",
            "view_id": False,
            "views": [(form_view.id, "form"), (tree_view.id, "tree")],
            "type": "ir.actions.act_window",
            "res_id": self.rec_visa_id.id,
            "target": "current",
            "nodestroy": True,
        }
