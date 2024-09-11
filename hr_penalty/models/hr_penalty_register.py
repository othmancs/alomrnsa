# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class HrPenaltyRegister(models.Model):
    _name = "hr.penalty.register"
    _description = "Hr Penalty Register"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "employee_id"

    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, tracking=True
    )
    department_id = fields.Many2one("hr.department", string="Department", tracking=True)
    job_id = fields.Many2one("hr.job", string="Job Position", tracking=True)
    pen_date = fields.Date("Date", default=fields.Date.today(), tracking=True)
    penalty_id = fields.Many2one(
        "hr.penalty", string="Penalty", required=True, tracking=True
    )
    punishment_ids = fields.Many2many(
        "hr.punishment", required=True, string="Punishment"
    )
    penalty_number = fields.Selection(
        [
            ("first_time", "First Time"),
            ("second_time", "Second Time"),
            ("third_time", "Third Time"),
            ("fourth_time", "Fourth Time"),
            ("fifth_time", "Fifth Time"),
        ],
        string="Penalty Number",
        tracking=True,
    )
    deduction_value = fields.Selection(
        [
            ("ded_salary", "Deduction from Salary"),
            ("ded_deduction", "Direct Payment Deduction"),
        ],
        default="ded_salary",
        string="Deduction Value",
        tracking=True,
    )
    deduction_amt = fields.Float(
        string="Deduction Amount", required=True, default=0.0, copy=False, tracking=True
    )
    decision = fields.Text("Decision", tracking=True)
    acc_committee_ids = fields.Many2many(
        "hr.employee",
        "emp_pen_rel",
        "emp_id",
        "penalty_id",
        string="Accounting Committee",
    )
    description = fields.Text("Description", tracking=True)
    journal_id = fields.Many2one(
        "account.journal", string="Journal", domain="[('type', 'in', ('bank', 'cash'))]"
    )
    payment_id = fields.Many2one("account.payment", string="Payment")
    termination_id = fields.Many2one("hr.employee.eos", string="Termination")
    payslip_id = fields.Many2one("hr.payslip", string="Payslip")
    warning_ids = fields.One2many("issue.warning", "pen_reg_id", string="Warning")
    is_warning = fields.Boolean("Is Warning ?", default=False)
    is_penal = fields.Boolean("Is Penalty ?", default=False)
    is_ded = fields.Boolean("Is Deduction ?", default=False)
    is_eos = fields.Boolean("Is Terminate ?", default=False)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("hr_officer", "HR Officer"),
            ("hr_manager", "HR Manager"),
            ("done", "Done"),
            ("refused", "Refused"),
        ],
        string="State",
        readonly=True,
        default="draft",
        tracking=True,
    )

    def action_hr_officer(self):
        self.write({"state": "hr_officer"})

    def action_hr_manager(self):
        self.write({"state": "hr_manager"})

    def action_done(self):
        for rec in self:
            punishment_termination = rec.punishment_ids.filtered(
                lambda p: p.p_type == "termination"
            )
            if not rec.termination_id and punishment_termination:
                termination_data = {
                    "name": "Penalty Termination",
                    "employee_id": rec.employee_id.id,
                    "contract_id": rec.employee_id.contract_id.id,
                    "department_id": rec.employee_id.department_id.id,
                    "job_id": rec.employee_id.job_id.id,
                    "eos_date": rec.pen_date,
                    "type": "termination",
                }
                data = self.env["hr.employee.eos"].create(termination_data)
                rec.termination_id = data.id
            rec.state = "done"

    def action_refused(self):
        for rec in self:
            rec.state = "refused"

    def action_redraft(self):
        for rec in self:
            rec.state = "draft"

    def unlink(self):
        for rec in self:
            if not rec.state == "draft":
                raise UserError(
                    _("You cannot remove the record which is in %s state!") % rec.state
                )
        return super(HrPenaltyRegister, self).unlink()

    def action_create_warning(self):
        self.ensure_one()
        ctx = dict(self._context) or {}
        ctx.update(
            {
                "default_employee_id": self.employee_id.id,
                "default_description": "Penalty Warning",
                "default_pen_reg_id": self.id,
            }
        )

        for punishment in self.punishment_ids.filtered(lambda p: p.p_type == "warning"):
            all_fields = self.env["issue.warning"].fields_get()
            warning_data = self.env["issue.warning"].default_get(all_fields)
            warning_data.update(
                {
                    "target_group": "employee",
                    "employee_id": self.employee_id.id,
                    "warning_action": "expiry",
                    "pen_reg_id": self.id,
                    "description": punishment.name,
                }
            )
            self.env["issue.warning"].create(warning_data)

        tree_view = self.env.ref("hr_warning.hr_warning_view_tree")
        form_view = self.env.ref("hr_warning.hr_warning_view_form")
        return {
            "type": "ir.actions.act_window",
            "name": _("Warning"),
            "res_model": "issue.warning",
            "view_mode": "form",
            "views": [(tree_view.id, "tree"), (form_view.id, "form")],
            "domain": [("id", "in", self.warning_ids.ids)],
            "context": ctx,
        }

    def action_create_payment(self):
        for rec in self:
            account_payment_data = {
                "partner_id": rec.employee_id.address_id.id,
                "amount": rec.deduction_amt,
                "payment_type": "inbound",
                "partner_type": "customer",
                "date": rec.pen_date,
                "journal_id": rec.journal_id.id,
            }
            if not rec.payment_id:
                rec.payment_id = self.env["account.payment"].create(
                    account_payment_data
                )

    @api.onchange("employee_id")
    def _onchange_employee(self):
        for rec in self:
            if rec.employee_id:
                rec.department_id = (
                    rec.employee_id.department_id
                    and rec.employee_id.department_id.id
                    or False
                )
                rec.job_id = (
                    rec.employee_id.job_id and rec.employee_id.job_id.id or False
                )
                pen_reg = self.search_count([("employee_id", "=", rec.employee_id.id)])
                if pen_reg == 1:
                    rec.write({"penalty_number": "second_time"})
                elif pen_reg == 2:
                    rec.write({"penalty_number": "third_time"})
                elif pen_reg == 3:
                    rec.write({"penalty_number": "fourth_time"})
                elif pen_reg == 4:
                    rec.write({"penalty_number": "fifth_time"})
                else:
                    rec.write({"penalty_number": "first_time"})

    @api.onchange("penalty_id", "penalty_number")
    def _onchange_penalty(self):
        for rec in self:
            if (
                rec.penalty_id
                and rec.penalty_id.first_time
                and rec.penalty_number == "first_time"
            ):
                rec.punishment_ids = rec.penalty_id.first_time

            if (
                rec.penalty_id
                and rec.penalty_id.second_time
                and rec.penalty_number == "second_time"
            ):
                rec.punishment_ids = rec.penalty_id.second_time

            if (
                rec.penalty_id
                and rec.penalty_id.third_time
                and rec.penalty_number == "third_time"
            ):
                rec.punishment_ids = rec.penalty_id.third_time

            if (
                rec.penalty_id
                and rec.penalty_id.fourth_time
                and rec.penalty_number == "fourth_time"
            ):
                rec.punishment_ids = rec.penalty_id.fourth_time

            if (
                rec.penalty_id
                and rec.penalty_id.fifth_time
                and rec.penalty_number == "fifth_time"
            ):
                rec.punishment_ids = rec.penalty_id.fifth_time

    @api.onchange("punishment_ids")
    def _onchange_punishment_ids(self):
        for rec in self:
            rec.is_warning = False
            rec.is_eos = False
            rec.is_penal = False
            rec.is_ded = False
            punishment_list = rec.punishment_ids.mapped("p_type")
            if "warning" in punishment_list:
                rec.is_warning = True
            if "termination" in punishment_list:
                rec.is_eos = True
            if "penalty" in punishment_list:
                rec.is_penal = True
                if rec.deduction_value == "ded_salary":
                    rec.is_ded = True

            deduction_amt = 0
            wage = self.employee_id.contract_id.wage
            for punishment in rec.punishment_ids.filtered(
                lambda p: p.p_type == "penalty"
            ):
                if punishment.punishment_type == "fixed_amount":
                    deduction_amt += punishment.penalty_amt
                else:
                    if (
                        punishment.punishment_type_amount == "duration"
                        and wage
                        and punishment.penalty_duration
                    ):
                        deduction_amt += wage / 30 * punishment.penalty_duration
                    elif (
                        punishment.punishment_type_amount == "percentage"
                        and wage
                        and punishment.penalty_percentage
                    ):
                        deduction_amt += wage / 100 * punishment.penalty_percentage
            rec.deduction_amt = deduction_amt

    @api.onchange("deduction_value")
    def _onchange_deduction_value(self):
        if self.deduction_value == "ded_salary":
            self.is_ded = True
        else:
            self.is_ded = False

    def view_payment(self):
        """
        Redirect On Payment
        """
        self.ensure_one()
        if self.payment_id.id:
            form_view = self.env.ref("account.view_account_payment_form")
            return {
                "type": "ir.actions.act_window",
                "name": _("Payment"),
                "res_model": "account.payment",
                "view_mode": "form",
                "views": [(form_view.id, "form")],
                "domain": [("id", "=", self.payment_id.id)],
                "res_id": self.payment_id.id,
                "context": self.env.context,
            }

    def view_termination(self):
        """
        Redirect On Termination
        """
        self.ensure_one()
        if self.termination_id:
            form_view = self.env.ref("saudi_hr_eos.view_employee_eos_form")
            return {
                "type": "ir.actions.act_window",
                "name": _("Termination"),
                "res_model": "hr.employee.eos",
                "view_mode": "form",
                "views": [(form_view.id, "form")],
                "res_id": self.termination_id.id,
                "context": self.env.context,
            }

    def view_payslip(self):
        """
        Redirect On Payslip
        """
        self.ensure_one()
        tree_view = self.env.ref("sync_hr_payroll.view_hr_payslip_tree")
        form_view = self.env.ref("sync_hr_payroll.view_hr_payslip_form")
        return {
            "type": "ir.actions.act_window",
            "name": _("Payslip"),
            "res_model": "hr.payslip",
            "view_mode": "form",
            "views": [(tree_view.id, "tree"), (form_view.id, "form")],
            "domain": [("pen_reg_ids", "=", self.id)],
            "context": self.env.context,
        }

    def view_warning(self):
        """
        Redirect On Warning
        """
        self.ensure_one()
        context = dict(self.env.context) or {}
        context.update({"default_pen_reg_id": self.id})
        if self.warning_ids:
            tree_view = self.env.ref("hr_warning.hr_warning_view_tree")
            form_view = self.env.ref("hr_warning.hr_warning_view_form")
            return {
                "type": "ir.actions.act_window",
                "name": _("Warning"),
                "res_model": "issue.warning",
                "view_mode": "form",
                "views": [(tree_view.id, "tree"), (form_view.id, "form")],
                "domain": [("id", "in", self.warning_ids.ids)],
                "context": context,
            }
