# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import time

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class ManpowerPlan(models.Model):
    _name = "manpower.plan"
    _order = "id desc"
    _inherit = ["mail.thread"]
    _description = "Manpower Planing"

    hof_id = fields.Many2one("hr.employee", "Head of Department", required=True)
    department_id = fields.Many2one("hr.department", "Department", required=True)
    fiscal_year_id = fields.Many2one(
        "year.year",
        "Plan Year",
        required=True,
        default=lambda self: self.env["year.year"].find(
            time.strftime("%Y-%m-%d"), True
        ),
    )
    plan_lines = fields.One2many("manpower.plan.line", "plan_id", "Plan Lines")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirm", "Waiting Approval"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        "Status",
        readonly=True,
        default="draft",
    )

    def name_get(self):
        """
        To retrieve the name, combination of `department name & fiscal year name`
        """
        result = []
        for plan in self:
            name = "".join(
                [plan.department_id.name or "", " - ", plan.fiscal_year_id.name or ""]
            )
            result.append((plan.id, name))
        return result

    @api.onchange("department_id")
    def onchange_department(self):
        """
        Change the value for `hof` based on selected department
        """
        self.hof_id = False
        if self.department_id:
            self.hof_id = self.department_id.manager_id.id

    def action_confirm_manpower(self):
        """
        Sent the status of generating manpower plan in confirm state
        """
        self.ensure_one()
        self.state = "confirm"
        self.message_post(
            message_type="email",
            subtype_xmlid="mail.mt_comment",
            body=_("Manpower plan confirm"),
        )

    def action_approve_manpower(self):
        """
        Sent the status of generating manpower plan in confirm state
        """
        self.ensure_one()
        self.state = "approved"
        self.message_post(
            message_type="email",
            subtype_xmlid="mail.mt_comment",
            body=_("Manpower plan approve."),
        )

    def action_reject_manpower(self):
        """
        Sent the status of generating manpower plan in confirm state
        """
        self.ensure_one()
        self.state = "rejected"
        self.message_post(
            message_type="email",
            subtype_xmlid="mail.mt_comment",
            body=_("Manpower plan reject"),
        )

    def action_set_draft(self):
        """
        Sent the status of generating manpower plan in drat state
        """
        self.ensure_one()
        self.state = "draft"
        self.message_post(
            message_type="email",
            subtype_xmlid="mail.mt_comment",
            body=_("Manpower plan draft"),
        )

    def unlink(self):
        for rec in self:
            if rec.state not in ["draft", "rejected"]:
                raise UserError(
                    _("you can not delete record when stage is %s.") % rec.state
                )
        return super(ManpowerPlan, self).unlink()


class ManpowerPlanLine(models.Model):
    _name = "manpower.plan.line"
    _order = "id desc"
    _description = "Manpower Plan Line"

    def _calculate_employees(self):
        """
        Calculate employees based on current_employees and leaving_employees
        """
        for line in self:
            calculated_emp = line.current_employees - line.leaving_employees
            line.calculated_employees = calculated_emp
            line.future_strength = (
                calculated_emp + line.critical_roles + line.expected_employees
            )

    @api.depends("joining_months")
    def _calculate_expected_emp(self):
        """
        Calculate Expected employees based on joining months
        """
        expected_employees = 0
        for rec in self:
            for month in rec.joining_months:
                expected_employees += month.joining_employees
            rec.expected_employees = expected_employees

    fiscal_year_id = fields.Many2one(
        "year.year",
        "Plan Year",
        required=True,
        default=lambda self: self.env["year.year"].find(
            time.strftime("%Y-%m-%d"), True
        ),
    )
    plan_id = fields.Many2one("manpower.plan", "Manpower Plan")
    job_id = fields.Many2one("hr.job", "Job", required=True)
    current_employees = fields.Integer("Current Employees")
    leaving_employees = fields.Integer("Forecast Leavers")
    calculated_employees = fields.Integer(
        "Forecast Employees", compute=_calculate_employees
    )
    critical_roles = fields.Integer("Critical Roles")
    expected_employees = fields.Integer(
        "Expected New Hires", compute=_calculate_expected_emp
    )
    future_strength = fields.Integer("Future Workforce", compute=_calculate_employees)
    joining_months = fields.One2many(
        "manpower.joining", "plan_line_id", "Joining Details"
    )
    no_of_employee = fields.Integer(related="job_id.no_of_employee")
    progress = fields.Float(string="Progress", compute="_progress_bar")
    job_requisition_id = fields.Many2one("hr.job.requisition")

    @api.constrains("joining_months")
    def check_duplicate_record(self):
        """
        Constraints for the record is overlaps for same month or not.
        """
        for rec in self:
            month_list = []
            for month in self.joining_months:
                if month.period_id.id not in month_list:
                    month_list.append(month.period_id.id)
                else:
                    raise ValidationError(
                        _("You already set %s month plan for %s job, Kindly check!!")
                        % (month.period_id.date_start.strftime("%B"), rec.job_id.name)
                    )

    def name_get(self):
        """
        To retrieve the name.`
        """
        result = []
        for plan in self:
            name = "".join([plan.job_id.name or ""])
            result.append((plan.id, name))
        return result

    @api.onchange("job_id")
    def onchange_job_id(self):
        """
        Onchange the value based on selected job
        """
        if self.job_id:
            self.current_employees = self.env["hr.employee"].search_count(
                [("job_id", "=", self.job_id.id)]
            )

    def create_or_update_requisition(self):
        """
        To use create Job Requisition
        """
        month_start_list = []
        month_end_list = []
        if self.joining_months:
            for month in self.joining_months:
                month_start_list.append(month.period_id.date_start)
                month_end_list.append(month.period_id.date_stop)
            if not self.job_requisition_id:
                job_req_id = self.env["hr.job.requisition"].create(
                    {
                        "name": self.job_id.name,
                        "department_id": self.job_id.department_id.id,
                        "job_id": self.job_id.id,
                        "min_salary": self.job_id.min_salary,
                        "max_salary": self.job_id.max_salary,
                        "start_date": sorted(month_start_list)[0],
                        "end_date": sorted(month_end_list)[-1],
                        "no_of_recruitment": self.expected_employees,
                    }
                )
                self.job_requisition_id = job_req_id.id

    def _progress_bar(self):
        """
        Calculate progress bar
        """
        for rec in self:
            total_emp = 0
            for month in rec.joining_months:
                total_emp += month.current_recruitment_emp
            rec.progress = (
                (total_emp * 100) / rec.expected_employees
                if rec.expected_employees
                else 0
            )


class ManpowerJoining(models.Model):
    _name = "manpower.joining"
    _order = "id desc"
    _description = "Manpower Joining"

    plan_line_id = fields.Many2one("manpower.plan.line", "Manpower Plan Line")
    period_id = fields.Many2one("year.period", "Month", required=True)
    joining_employees = fields.Integer("Joining Employees")
    current_recruitment_emp = fields.Integer(
        "Current Recruitment", compute="_calculate_cur_recruitment"
    )
    progress = fields.Float(string="Progress", compute="_progress_bar")

    def _calculate_cur_recruitment(self):
        """
        Calculate employees based on current recruitment
        """
        for rec in self:
            rec.current_recruitment_emp = self.env["hr.employee"].search_count(
                [
                    ("date_of_join", ">=", rec.period_id.date_start),
                    ("date_of_join", "<=", rec.period_id.date_stop),
                    ("job_id", "=", rec.plan_line_id.job_id.id),
                ]
            )

    def _progress_bar(self):
        """
        Calculate Progress bar
        """
        for rec in self:
            rec.progress = 0.0
            if rec.current_recruitment_emp > 0 and rec.joining_employees > 0:
                rec.progress = (
                    rec.current_recruitment_emp * 100
                ) / rec.joining_employees
