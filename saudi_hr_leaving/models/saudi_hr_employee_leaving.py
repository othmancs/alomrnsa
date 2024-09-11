# -*- coding: utf-8 -*-
# Part of odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

leaving_states = [
    ("draft", "Draft"),
    ("confirm", "Waiting Approval"),
    ("approve", "Approved"),
    ("validate", "Validated"),
    ("refuse", "Refused"),
]


class HREmployeeLeaving(models.Model):
    _name = "hr.employee.leaving"
    _inherit = ["mail.thread"]
    _description = "HR Employee Leaving"

    def unlink(self):
        """
        To remove the record, which is in 'draft' states
        """
        for object in self:
            if object.state in ["confirm", "validate", "approve", "refuse"]:
                raise UserError(
                    _("You cannot remove the record which is in %s state!")
                    % object.state
                )
        return super(HREmployeeLeaving, self).unlink()

    @api.constrains("notice_start_date", "requested_date")
    def _check_start_date(self):
        for rec in self:
            if (
                rec.notice_start_date
                and rec.requested_date
                and rec.notice_start_date <= rec.requested_date
            ):
                raise ValidationError(
                    _("Notice Start Date must be greater than Requested Date")
                )

    @api.constrains("notice_end_date", "notice_start_date")
    def _check_end_date(self):
        for rec in self:
            if (
                rec.notice_end_date
                and rec.notice_start_date
                and rec.notice_end_date < rec.notice_start_date
            ):
                raise ValidationError(
                    _("Notice End Date must be greater than Notice Start Date")
                )

    @api.constrains("exit_date", "notice_end_date")
    def _check_exit_date(self):
        for rec in self:
            if (
                rec.notice_end_date
                and rec.exit_date
                and rec.exit_date < rec.notice_end_date
            ):
                raise ValidationError(
                    _("Exit Date must be greater than Notice End Date")
                )

    employee_id = fields.Many2one(
        "hr.employee",
        "Employee",
        required=True,
        default=lambda self: self.env["hr.employee"].get_employee(),
    )
    department_id = fields.Many2one("hr.department", "Department", readonly=True)
    branch_id = fields.Many2one("hr.branch", "Office", readonly=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        readonly=True,
        default=lambda self: self.env.user.company_id,
    )
    reason = fields.Char("Reason", size=128, required=True)
    requested_date = fields.Date(
        "Requested Date", default=datetime.strftime(datetime.now(), "%Y-%m-%d")
    )
    notice_start_date = fields.Date("Notice Start Date")
    notice_end_date = fields.Date("Notice End Date")
    exit_date = fields.Date("Exit Date", compute="compute_exit_date", store=True)
    contact_person = fields.Many2one("res.users", "Contact Person")
    description = fields.Text("Description", required=True)
    state = fields.Selection(leaving_states, "Status", tracking=True, default="draft")
    approved_date = fields.Datetime(
        "Approved Date", readonly=True, tracking=True, copy=False
    )
    approved_by = fields.Many2one(
        "res.users", "Approved By", readonly=True, tracking=True, copy=False
    )
    refused_by = fields.Many2one(
        "res.users", "Refused By", readonly=True, tracking=True, copy=False
    )
    refused_date = fields.Datetime(
        "Refused Date", readonly=True, tracking=True, copy=False
    )

    def _track_subtype(self, init_values):
        self.ensure_one()
        if "state" in init_values and self.state == "draft":
            return self.env.ref("saudi_hr_leaving.mt_employee_leaving_new")
        elif "state" in init_values and self.state == "confirm":
            return self.env.ref("saudi_hr_leaving.mt_employee_leaving_confirm")
        elif "state" in init_values and self.state == "validate":
            return self.env.ref("saudi_hr_leaving.mt_employee_leaving_validate")
        elif "state" in init_values and self.state == "approve":
            return self.env.ref("saudi_hr_leaving.mt_employee_leaving_approve")
        elif "state" in init_values and self.state == "refuse":
            return self.env.ref("saudi_hr_leaving.mt_employee_leaving_cancel")
        return super(HREmployeeLeaving, self)._track_subtype(init_values)

    def name_get(self):
        """
        Retrieves the names of employees.

        :return: A list of tuples containing the ID and name of each employee.
        The name is constructed by appending the word "Leaving" to the employee's
        name if it exists, otherwise just "Leaving" is used.
        """
        res = []
        for leave in self:
            name = "".join([leave.employee_id.name or "", " Leaving"])
            res.append((leave.id, name))
        return res

    @api.onchange("employee_id")
    def onchange_employee(self):
        """
        Updates the department, company, and branch based on the selected employee.
        """
        self.department_id = self.employee_id.department_id.id or False
        self.company_id = self.employee_id.company_id.id or False
        self.branch_id = self.employee_id.branch_id or False

    @api.onchange("notice_start_date")
    def onchange_notice_start_date(self):
        """
        Calculates the `notice_end_date` based on the `notice_start_date` by adding 60 days.
        """
        if self.notice_start_date:
            self.notice_end_date = self.notice_start_date + timedelta(days=60)

    @api.depends("notice_end_date")
    def compute_exit_date(self):
        """
        Sets the `exit_date` field based on the value of the `notice_end_date` field.
        """
        for rec in self:
            rec.exit_date = rec.notice_end_date or False

    def leaving_confirm(self):
        """
        Sets the state of a leaving request to 'confirm'.
        """
        self.ensure_one()
        self.state = "confirm"

    def leaving_approve(self):
        """
        Processes leaving requests for employees, updating their status and sending an email notification.
        """
        self.ensure_one()
        today = datetime.today()
        if self.employee_id:
            department = self.env["hr.department"].search(
                [("manager_id", "=", self.employee_id.id)]
            )
            if department:
                department.write({"manager_id": False})
            if self.employee_id.user_id:
                self.employee_id.user_id.write({"active": False})
            self.employee_id.write(
                {
                    "employee_status": "quit",
                    "date_of_leave": self.notice_end_date,
                    "state_selection": "non_active",
                    "active": False,
                }
            )
            contract_ids = self.employee_id._get_contracts(
                self.notice_start_date, self.notice_end_date, states=["open"]
            )
            if contract_ids:
                contract_ids.write(
                    {
                        "notice_start_date": self.notice_start_date or False,
                        "notice_end_date": self.notice_end_date or False,
                        "is_leaving": True,
                    }
                )
        self.write(
            {"state": "approve", "approved_by": self.env.uid, "approved_date": today}
        )
        try:
            template_id = self.env.ref(
                "saudi_hr_leaving.email_template_resigned_emp_aknowledgement"
            )
        except ValueError:
            template_id = False
        if template_id:
            template_id.send_mail(self.id, force_send=True)

    def leaving_validate(self):
        """
        Sets the status of a leaving request to 'validate'.
        """
        self.ensure_one()
        self.state = "validate"

    def leaving_refuse(self):
        """
        Updates the state of a record to 'refuse' and logs the user and date of refusal.
        """
        self.ensure_one()
        self.write(
            {
                "state": "refuse",
                "refused_by": self.env.uid,
                "refused_date": datetime.today(),
            }
        )

    def set_draft(self):
        """
        Sets a record to draft state and updates related fields if an employee is associated with it.
        """
        self.ensure_one()
        if self.employee_id:
            self.employee_id.date_of_leave = False
            contract_id = self.employee_id._get_contracts(
                self.notice_start_date, self.notice_end_date, states=["open"]
            )
            if contract_id:
                contract_id.write(
                    {
                        "notice_start_date": False,
                        "notice_end_date": False,
                        "is_leaving": False,
                    }
                )
        self.state = "draft"
