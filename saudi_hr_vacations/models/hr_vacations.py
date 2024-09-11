# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil import relativedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class HRVacation(models.Model):
    _name = "hr.vacation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "HR Vacation"

    def _default_employee(self):
        return self.env.user.employee_id

    name = fields.Char(string="Name", copy=False, required=True, default="New")
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, default=_default_employee
    )
    department_id = fields.Many2one(
        "hr.department",
        string="Department",
        related="employee_id.department_id",
        store=True,
    )
    job_id = fields.Many2one(
        "hr.job",
        "Job Position",
        readonly=True,
        related="employee_id.job_id",
        store=True,
    )
    branch_id = fields.Many2one(
        "hr.branch",
        "Office",
        readonly=True,
        related="employee_id.branch_id",
        store=True,
    )

    date_start = fields.Date(string="Start Date", required=True, tracking=True)
    date_to = fields.Date(string="End Date", required=True, tracking=True)
    return_to_work_date = fields.Date(
        string="Return to Work Date", copy=False, tracking=True
    )
    vacation_days = fields.Float(
        string="No. of Vacation Days",
        compute="calculate_vacation_days",
        copy=False,
        tracking=True,
    )
    remaining_vacation_days = fields.Float(
        string="Remaining Vacation Days",
        compute="compute_remaining_vacation_days",
        tracking=True,
    )
    hr_leave_ids = fields.One2many("hr.leave", "hr_vacation_id", string="Leaves")
    visa_ids = fields.One2many("hr.visa", "hr_vacation_id", string="Visa")
    advance_salary_ids = fields.One2many(
        "hr.advance.salary", "hr_vacation_id", string="Advance salary"
    )
    direct_manager_approved_by = fields.Many2one(
        "res.users", string="Direct Manager Approval By", tracking=True, copy=False
    )
    financial_manager_approved_by = fields.Many2one(
        "res.users", string="Financial Manager Approval By", tracking=True, copy=False
    )
    hr_manager_approved_by = fields.Many2one(
        "res.users", string="HR Manager Approval By", tracking=True, copy=False
    )
    cancelled_by = fields.Many2one(
        "res.users", string="Cancelled By", tracking=True, copy=False
    )
    direct_manager_approved_date = fields.Datetime(
        "Direct Manager Approved Date", tracking=True, copy=False
    )
    financial_manager_approved_date = fields.Datetime(
        "Financial Manager Approved Date", tracking=True, copy=False
    )
    hr_manager_approved_date = fields.Datetime(
        "HR Manager Approved Date", tracking=True, copy=False
    )
    cancelled_date = fields.Datetime("Cancelled Date", tracking=True, copy=False)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirm", "Confirm"),
            ("direct_manager", "Direct Manager Approved"),
            ("finance_manager", "Finance Manager Approved"),
            ("hr_manager", "HR Manager Approved"),
            ("join_work_after_vacation", "Join Work After Vacation"),
            ("cancel", "Cancel"),
        ],
        string="Status",
        default="draft",
        copy=False,
        tracking=True,
    )

    @api.depends("date_start", "date_to")
    def compute_remaining_vacation_days(self):
        vacations_allocation = self.env["hr.vacations.allocation"]
        for rec in self:
            rec.remaining_vacation_days = 0
            if rec.date_start and rec.date_to:
                vacations_allocation_id = vacations_allocation.search(
                    [
                        ("employee_id", "=", rec.employee_id.id),
                        ("from_date", "<=", rec.date_start),
                        ("to_date", ">=", rec.date_to),
                        ("state", "=", "validate"),
                    ]
                )
                if vacations_allocation_id:
                    difference = rec.date_to - rec.date_start
                    rec.remaining_vacation_days = (
                        vacations_allocation_id.remaining_duration - difference.days
                    )

    @api.constrains("date_start", "date_to")
    def check_date(self):
        for rec in self:
            if rec.date_start > rec.date_to:
                raise UserError("End Date must be greater than of Start Date.")

    @api.constrains("return_to_work_date", "date_start")
    def check_return_work_date(self):
        for rec in self:
            if (
                rec.return_to_work_date
                and rec.date_start
                and rec.return_to_work_date < rec.date_start
            ):
                raise UserError(
                    "Return Work Date must be greater than of Vacation Start Date."
                )
            if (
                rec.return_to_work_date
                and rec.return_to_work_date < fields.Date.today()
                and not self.user_has_groups("hr.group_hr_user")
                and not self.user_has_groups("hr.group_hr_manager")
            ):
                raise UserError(
                    "You can not set Return to work date less than to today."
                )

    @api.constrains("date_start", "date_to", "state", "employee_id")
    def _check_date(self):
        for vacation in self.filtered("employee_id"):
            domain = [
                ("date_start", "<", vacation.date_to),
                ("date_to", ">", vacation.date_start),
                ("employee_id", "=", vacation.employee_id.id),
                ("id", "!=", vacation.id),
                ("state", "not in", ["cancel"]),
            ]
            nholidays = self.search_count(domain)
            if nholidays:
                raise ValidationError(
                    _(
                        "You can not set multiple vacations that overlaps on the same day for the same employee."
                    )
                )

    def calculate_vacation_days(self):
        for rec in self:
            if rec.return_to_work_date:
                working_hours = self.employee_id.resource_calendar_id.default_get(
                    "attendance_ids"
                )["attendance_ids"]
                weekday_list = []
                for weekday in working_hours:
                    if weekday[2].get("dayofweek") not in weekday_list:
                        weekday_list.append(weekday[2].get("dayofweek"))

                return_to_work_date = rec.return_to_work_date
                while (
                    str(return_to_work_date.weekday()) == "0"
                    or str(return_to_work_date.weekday()) not in weekday_list
                ):
                    return_to_work_date = (
                        return_to_work_date - relativedelta.relativedelta(days=1)
                    )
                rec.vacation_days = (return_to_work_date - rec.date_start).days + 1

            elif rec.date_start and rec.date_to:
                rec.vacation_days = (rec.date_to - rec.date_start).days
            else:
                rec.vacation_days = 0.0

    def _add_followers(self, partner_ids=[]):
        """
        Add employee and manager in followers
        """
        self.message_subscribe(partner_ids=partner_ids)

    @api.model_create_multi
    def create(self, values):
        """
        Override create method
        """
        for vals in values:
            vals["name"] = self.env["ir.sequence"].next_by_code("vacation_request")
        records = super(HRVacation, self).create(vals)
        for rec in records:
            if rec.employee_id:
                partner_ids = (
                    rec.employee_id.user_id
                    and [rec.employee_id.user_id.partner_id.id]
                    or []
                )
                rec._add_followers(partner_ids)
        return records

    def action_confirm(self):
        for rec in self:
            rec.state = "confirm"
            partner_ids = []
            if rec.employee_id.parent_id and rec.employee_id.parent_id.user_id:
                partner_ids.append(rec.employee_id.parent_id.user_id.partner_id.id)
            if rec.employee_id.leave_manager_id:
                partner_ids.append(rec.employee_id.leave_manager_id.partner_id.id)
            rec._add_followers(partner_ids)

    def action_direct_manager_approval(self):
        for rec in self:
            rec.state = "direct_manager"
            rec.direct_manager_approved_by = self.env.uid
            rec.direct_manager_approved_date = fields.Datetime.now()

            finance_groups_config_ids = self.env["hr.groups.configuration"].search(
                [
                    ("branch_id", "=", rec.employee_id.branch_id.id),
                    ("finance_ids", "!=", False),
                ]
            )
            partner_ids = (
                finance_groups_config_ids
                and [
                    employee.user_id.partner_id.id
                    for employee in finance_groups_config_ids.sudo().finance_ids
                    if employee.user_id
                ]
                or []
            )
            rec._add_followers(partner_ids)

    def action_finance_manager_approval(self):
        for rec in self:
            rec.state = "finance_manager"
            rec.financial_manager_approved_by = self.env.uid
            rec.financial_manager_approved_date = fields.Datetime.now()

            hr_groups_config_ids = self.env["hr.groups.configuration"].search(
                [
                    ("branch_id", "=", rec.employee_id.branch_id.id),
                    ("hr_ids", "!=", False),
                ]
            )
            partner_ids = (
                hr_groups_config_ids
                and [
                    employee.user_id.partner_id.id
                    for employee in hr_groups_config_ids.sudo().hr_ids
                    if employee.user_id
                ]
                or []
            )
            rec._add_followers(partner_ids)

    def action_hr_manager_approval(self):
        for rec in self:
            rec.state = "hr_manager"
            rec.hr_manager_approved_by = self.env.uid
            rec.hr_manager_approved_date = fields.Datetime.now()

    def action_join_to_work(self):
        for rec in self:
            if not rec.return_to_work_date:
                raise UserError(
                    _("Kindly provide the 'Return to Work Date' information.")
                )
            rec.state = "join_work_after_vacation"

    def action_cancel(self):
        for rec in self:
            rec.state = "cancel"
            rec.cancelled_by = self.env.uid
            rec.cancelled_date = fields.Datetime.now()

    def action_changed_enddate(self):
        context = dict(self._context)
        context.update(
            {"default_vacation_id": self.id, "default_enddate": self.date_to}
        )
        compose_form = self.env.ref(
            "saudi_hr_vacations.view_hr_vacation_change_enddate_form", False
        ).id
        return {
            "name": _("Update EndDate"),
            "view_mode": "form",
            "res_model": "change.enddate.wizard",
            "view_id": compose_form,
            "type": "ir.actions.act_window",
            "context": context,
            "target": "new",
        }
