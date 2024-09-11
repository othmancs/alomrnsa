# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime

from odoo import _, fields, models
from odoo.exceptions import UserError

clearance_states = [
    ("draft", "Draft"),
    ("confirm", "Waiting Manager Approval"),
    ("emp_dept", "Waiting Finance Approval"),
    ("finance_dept", "Waiting Admin Approval"),
    ("admin_dept", "Waiting Done"),
    ("done", "Done"),
    ("refuse", "Refused"),
]

department_types = [
    ("admin", "Admin"),
    ("finance", "Finance"),
    ("emp_dept", "Employee Department"),
]

item_state = [("yes", "YES"), ("no", "NO"), ("na", "N/A")]

clearance_context = False


class ClearanceDepartmentData(models.Model):
    _name = "clearance.department.data"
    _description = "Clearance Department Data"
    _rec_name = "item"

    department_type = fields.Selection(department_types, "Department Type")
    item = fields.Char("Item", required="True", translate=True)
    item_state = fields.Selection(item_state, "Status", required="True", default="na")
    active = fields.Boolean("Active", default=True)


class ClearanceDepartment(models.Model):
    _name = "clearance.department"
    _description = "Clearance Department"

    admin_dept_id = fields.Many2one("hr.employee.clearance", "Admin Department")
    finance_dept_id = fields.Many2one("hr.employee.clearance", "Finance Department")
    employee_dept_id = fields.Many2one("hr.employee.clearance", "Employee Department")
    department_type = fields.Selection(department_types, "Department Type")
    item = fields.Char("Item", required="True", translate=True)
    item_state = fields.Selection(item_state, "Status", required="True")
    handled_by = fields.Many2one("hr.employee", "Handled by")
    remarks = fields.Char("Remarks")


class HrEmployeeClearance(models.Model):
    _name = "hr.employee.clearance"
    _inherit = "mail.thread"
    _description = "Employee Clearance"
    _rec_name = "employee_name"

    def unlink(self):
        """
        To remove the record, which is not in 'confirm','done' state
        """
        for objects in self:
            if objects.state in ["confirm", "done"]:
                raise UserError(
                    _("You cannot remove the record which is in %s state!")
                    % objects.state
                )
        return super(HrEmployeeClearance, self).unlink()

    # Fields Hr Employee Clearance
    employee_id = fields.Many2one(
        "hr.employee",
        "Employee",
        required=True,
        default=lambda self: self.env["hr.employee"].get_employee(),
    )
    line_manager_id = fields.Many2one("hr.employee", "Manager")
    employee_name = fields.Char(string="Name", related="employee_id.name")
    seniority_date = fields.Date("Seniority Date", default=time.strftime("%Y-%m-%d"))
    last_working_day = fields.Date(
        "Last Day of Work", related="employee_id.date_of_leave", store=True
    )
    location = fields.Many2one(
        "hr.branch",
        "Location",
        readonly="True",
        related="employee_id.branch_id",
        store=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        readonly=True,
        default=lambda self: self.env.user.company_id,
    )
    passport_no = fields.Char("Passport No", readonly="True")
    department_id = fields.Many2one(
        "hr.department", "Department", related="employee_id.department_id", store=True
    )
    approved_date = fields.Datetime("Approved Date", readonly=True, copy=False)
    approved_by = fields.Many2one("res.users", "Approved by", readonly=True, copy=False)
    state = fields.Selection(clearance_states, "Status", default="draft")
    is_employee_leaving = fields.Boolean("Last Clearance", default=False, tracking=True)
    eos_count = fields.Integer("EOS Count", compute="_compute_eos_count")
    eos_type = fields.Selection(
        [
            ("resignation", "Resignation"),
            ("termination", "Termination"),
            ("death", "Death"),
        ],
        "EOS Type",
    )
    admin_dept_ids = fields.One2many(
        "clearance.department", "admin_dept_id", "Admin Departments"
    )
    finance_dept_ids = fields.One2many(
        "clearance.department", "finance_dept_id", "Finance Departments"
    )
    employee_dept_ids = fields.One2many(
        "clearance.department", "employee_dept_id", "Employee Department"
    )

    def write(self, vals):
        if (
            (
                vals.get("admin_dept_ids")
                or vals.get("finance_dept_ids")
                or vals.get("employee_dept_ids")
            )
            and self.env.user.employee_id
            and not self.user_has_groups("hr.group_hr_user")
            and not self.user_has_groups("saudi_hr.group_line_manager")
        ):
            raise UserError(
                _(
                    "You are not modify departments data please contact your administrator."
                )
            )
        return super(HrEmployeeClearance, self).write(vals)

    def _compute_eos_count(self):
        self.eos_count = self.env["hr.employee.eos"].search_count(
            [("employee_id", "=", self.employee_id.id)]
        )

    def clearance_done(self):
        """
        Sent the status of generating his/her clearance in Done state
        """
        self.ensure_one()
        self.write(
            {
                "state": "done",
                "approved_by": self.env.user.id,
                "approved_date": datetime.today(),
            }
        )

    def generate_eos(self):
        """
        Generate EOS for the employee
        """
        for rec in self:
            if rec.is_employee_leaving:
                eos_ids = self.env["hr.employee.eos"].search(
                    [("employee_id", "=", self.employee_id.id)]
                )
                if eos_ids:
                    raise UserError(
                        _("%s's EOS is already Generated.") % self.employee_id.name
                    )
                else:
                    self.env["hr.employee.eos"].create(
                        {
                            "name": self.employee_name
                            and self.employee_name + " " + "EOS"
                            or False,
                            "employee_id": self.employee_id
                            and self.employee_id.id
                            or False,
                            "contract_id": self.employee_id
                            and self.employee_id.contract_id
                            and self.employee_id.contract_id.id
                            or False,
                            "eos_date": datetime.today().date(),
                            "type": self.eos_type or False,
                        }
                    )

    def _add_followers(self):
        """
        Add employee and manager in followers
        """
        partner_ids = False
        for rec in self:
            if rec.state == "confirm":
                hr_groups_config_ids = (
                    self.env["hr.groups.configuration"]
                    .sudo()
                    .search(
                        [("branch_id", "=", self.location.id), ("hr_ids", "!=", False)]
                    )
                )
                if hr_groups_config_ids:
                    partner_ids = (
                        hr_groups_config_ids
                        and [
                            employee.user_id.partner_id.id
                            for employee in hr_groups_config_ids.hr_ids
                            if employee.user_id
                        ]
                        or []
                    )
            elif rec.state == "emp_dept":
                finance_groups_config_ids = (
                    self.env["hr.groups.configuration"]
                    .sudo()
                    .search(
                        [
                            ("branch_id", "=", self.location.id),
                            ("finance_ids", "!=", False),
                        ]
                    )
                )
                if finance_groups_config_ids:
                    partner_ids = (
                        finance_groups_config_ids
                        and [
                            employee.user_id.partner_id.id
                            for employee in finance_groups_config_ids.finance_ids
                            if employee.user_id
                        ]
                        or []
                    )
            elif rec.state == "finance_dept":
                admin_groups_config_ids = (
                    self.env["hr.groups.configuration"]
                    .sudo()
                    .search(
                        [
                            ("branch_id", "=", self.location.id),
                            ("admin_ids", "!=", False),
                        ]
                    )
                )
                if admin_groups_config_ids:
                    partner_ids = (
                        admin_groups_config_ids
                        and [
                            employee.user_id.partner_id.id
                            for employee in admin_groups_config_ids.admin_ids
                            if employee.user_id
                        ]
                        or []
                    )
        self.message_subscribe(partner_ids=partner_ids)

    def clearance_cancel(self):
        """
        Sent the status of generating his/her clearance in Cancel state
        """
        self.ensure_one()
        self.state = "refuse"

    def clearance_confirm(self):
        """
        Sent the status of generating his/her clearance in Confirm state
        """
        self.ensure_one()
        self.write(
            {"state": "confirm", "line_manager_id": self.employee_id.parent_id.id}
        )
        clearance_dept_ids = self.env["clearance.department.data"].search(
            [("department_type", "=", "emp_dept")]
        )
        for clearance_dept_id in clearance_dept_ids:
            self.env["clearance.department"].create(
                {
                    "department_type": clearance_dept_id.department_type,
                    "item": clearance_dept_id.item,
                    "item_state": clearance_dept_id.item_state,
                    "employee_dept_id": self.id,
                }
            )
        self._add_followers()

    def set_to_draft(self):
        """
        Sent the status of generating his/her clearance in Set to Draft state
        """
        self.ensure_one()
        self.state = "draft"

    def clearance_next(self):
        for rec in self:
            if rec.state == "confirm":
                if "na" in rec.employee_dept_ids.mapped("item_state"):
                    raise UserError(_("Please Update Employee Department Status."))
                clearance_dept_ids = self.env["clearance.department.data"].search(
                    [("department_type", "=", "finance")]
                )
                for clearance_dept_id in clearance_dept_ids:
                    self.env["clearance.department"].create(
                        {
                            "department_type": clearance_dept_id.department_type,
                            "item": clearance_dept_id.item,
                            "item_state": clearance_dept_id.item_state,
                            "finance_dept_id": self.id,
                        }
                    )

                rec.state = "emp_dept"
                self._add_followers()
            elif rec.state == "emp_dept":
                if "na" in rec.finance_dept_ids.mapped("item_state"):
                    raise UserError(_("Please Update Finance Department Status."))
                rec.state = "finance_dept"
                clearance_dept_ids = self.env["clearance.department.data"].search(
                    [("department_type", "=", "admin")]
                )
                for clearance_dept_id in clearance_dept_ids:
                    self.env["clearance.department"].create(
                        {
                            "department_type": clearance_dept_id.department_type,
                            "item": clearance_dept_id.item,
                            "item_state": clearance_dept_id.item_state,
                            "admin_dept_id": self.id,
                        }
                    )
                self._add_followers()
            elif rec.state == "finance_dept":
                if "na" in rec.admin_dept_ids.mapped("item_state"):
                    raise UserError(_("Please Update HR Department Status."))
                rec.state = "admin_dept"

    def action_view_eos(self):
        eos_ids = self.env["hr.employee.eos"].search(
            [("employee_id", "=", self.employee_id.id)]
        )
        tree_view = self.env.ref("saudi_hr_eos.view_employee_eos_tree")
        form_view = self.env.ref("saudi_hr_eos.view_employee_eos_form")
        return {
            "type": "ir.actions.act_window",
            "name": _("Employee Eos"),
            "res_model": "hr.employee.eos",
            "view_mode": "from",
            "views": [(tree_view.id, "tree"), (form_view.id, "form")],
            "domain": [("id", "in", eos_ids.ids)],
        }
