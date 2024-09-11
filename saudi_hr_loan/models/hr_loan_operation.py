# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import time
from datetime import datetime

from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class HrLoanOperation(models.Model):
    _name = "hr.loan.operation"
    _inherit = ["mail.thread", "analytic.mixin"]
    _description = "Loan Operation"

    def _get_employee(self):
        loan_ids = self.env["hr.loan"].search([("state", "=", "approve")])
        return loan_ids.mapped("employee_id.id")

    name = fields.Char(
        "Name",
        required=True,
        copy=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
        index=True,
        default=lambda self: _("New"),
    )
    loan_operation_type = fields.Selection(
        [
            ("skip_installment", "Skip Installment"),
            ("increase_amount", "Increase Loan Amount"),
            ("loan_payment", "Loan Payment"),
        ],
        required=True,
        default="skip_installment",
    )
    skip_reason = fields.Char("Reason to Skip", tracking=True)
    loan_id = fields.Many2one(
        "hr.loan",
        "Loan",
        domain="[('employee_id','=',employee_id), ('state','=', 'approve')]",
        required=True,
        tracking=True,
    )
    employee_id = fields.Many2one(
        "hr.employee",
        "Employee",
        required=True,
        tracking=True,
        domain=lambda self: self._get_employee_domain(),
    )
    department_id = fields.Many2one(
        "hr.department",
        string="Department",
        related="employee_id.department_id",
        store=True,
    )
    branch_id = fields.Many2one(
        "hr.branch",
        "Office",
        readonly=True,
        related="employee_id.branch_id",
        store=True,
    )
    effective_date = fields.Date("Effective Date", tracking=True)
    current_loan_amount = fields.Float(
        "Current Loan Amount", related="loan_id.loan_amount", readonly=True
    )
    amount_to_pay = fields.Float(
        "Amount to Pay", related="loan_id.amount_to_pay", readonly=True
    )
    loan_amount = fields.Float("Increase Loan Amount", copy=False)
    loan_payment_type = fields.Selection(
        [("fully", "Fully Payment"), ("partially", "Partially Payment")],
        default="fully",
        copy=False,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        readonly=False,
        default=lambda self: self.env.user.company_id,
    )
    payment_amount = fields.Float("Payment Amount")
    payment_type = fields.Selection(
        [("by_payslip", "By Payslip"), ("by_account", "By Account")],
        default="by_payslip",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirm", "Confirm"),
            ("open", "Waiting Approval"),
            ("approve", "Approved"),
            ("cancel", "Cancelled"),
            ("refuse", "Refused"),
            ("done", "Done"),
        ],
        default="draft",
        copy=False,
    )
    treasury_account_id = fields.Many2one("account.account", string="Treasury Account")
    emp_account_id = fields.Many2one("account.account", string="Employee Loan Account")
    journal_id = fields.Many2one(
        "account.journal",
        "Journal",
        default=lambda self: self.env["account.journal"].search(
            [("type", "=", "general")], limit=1
        ),
    )
    move_id = fields.Many2one(
        "account.move", "Accounting Entry", readonly=True, copy=False
    )
    approved_by = fields.Many2one("res.users", "Approved by", readonly=True, copy=False)
    refused_by = fields.Many2one("res.users", "Refused by", readonly=True, copy=False)
    approved_date = fields.Datetime(string="Approved on", readonly=True, copy=False)
    refused_date = fields.Datetime(string="Refused on", readonly=True, copy=False)
    accounting_info = fields.Boolean(
        "Accounting Info", default=False, compute="compute_accounting_info"
    )
    operation_applied = fields.Boolean("Effect Applied on Loan?", default=False)
    loan_next_schedule_id = fields.Many2one(
        "hr.employee.loan.line", string="Loan Schedule", copy=False
    )

    def _get_employee_domain(self):
        domain = []
        leave_allocation_obj = self.env["hr.loan"]
        employees = leave_allocation_obj.search([("state", "=", "approve")]).mapped(
            "employee_id"
        )
        domain.append(("id", "in", employees.ids))
        return domain

    @api.onchange("loan_id")
    def onchange_loan(self):
        for rec in self:
            rec.analytic_distribution = (
                rec.loan_id and [(6, 0, rec.loan_id.analytic_distribution)] or {}
            )
            rec.treasury_account_id = (
                rec.loan_id and rec.loan_id.treasury_account_id.id or False
            )
            rec.emp_account_id = rec.loan_id and rec.loan_id.emp_account_id.id or False

    @api.depends("loan_operation_type", "state", "payment_type")
    def compute_accounting_info(self):
        for rec in self:
            if (
                rec.state in ["open", "approve"]
                and rec.loan_operation_type == "increase_amount"
            ):
                rec.accounting_info = True
            elif (
                rec.state in ["open", "approve"]
                and rec.loan_operation_type == "loan_payment"
                and rec.payment_type == "by_account"
            ):
                rec.accounting_info = True
            else:
                rec.accounting_info = False

    def check_loan_operation_req(self, employee, effective_date, type):
        if effective_date:
            loan_operation_ids = self.search(
                [
                    ("state", "in", ["confirm", "open", "approve"]),
                    ("employee_id", "=", employee.id),
                    ("id", "!=", self.id),
                    ("loan_id", "=", self.loan_id.id),
                ]
            )
            for rec in loan_operation_ids:
                if (
                    rec.loan_operation_type == "increase_amount"
                    and type != "increase_amount"
                    and rec.effective_date.month == effective_date.month
                    and rec.effective_date.year == effective_date.year
                ):
                    raise ValidationError(
                        _(
                            "During this month %s has already request for increase amount so kindly check loan operation request!!"
                            % employee.name
                        )
                    )
                elif (
                    rec.loan_operation_type == "skip_installment"
                    and rec.effective_date.month == effective_date.month
                    and rec.effective_date.year == effective_date.year
                ):
                    raise ValidationError(
                        _(
                            "During this month %s has already request for skip installment so kindly check loan operation request!!"
                            % employee.name
                        )
                    )
                elif (
                    rec.loan_operation_type == "loan_payment"
                    and rec.effective_date.month == effective_date.month
                    and rec.effective_date.year == effective_date.year
                ):
                    raise ValidationError(
                        _(
                            "During this month %s has already request for loan payment so kindly check loan operation request!!"
                            % employee.name
                        )
                    )

    @api.constrains("loan_amount", "payment_amount")
    def check_loan_amount(self):
        """
        Check increase loan amount 0 or not
        """
        for rec in self:
            if rec.loan_operation_type == "increase_amount" and rec.loan_amount <= 0:
                raise ValidationError(
                    _("Increase Loan Amount Must be Greater than 0!!")
                )
            elif (
                rec.loan_operation_type == "loan_payment"
                and rec.loan_payment_type == "partially"
                and rec.payment_amount <= 0
            ):
                raise ValidationError(_("Pay Loan Amount Must be Greater than 0!!"))

    @api.onchange("loan_payment_type")
    def onchange_loan_payment_type(self):
        if self.loan_payment_type:
            self.payment_amount = False

    @api.onchange("employee_id")
    def _onchange_employee(self):
        if self.employee_id:
            loan_id = self.env["hr.loan"].search(
                [("state", "=", "approve"), ("employee_id", "=", self.employee_id.id)]
            )
            if not loan_id:
                raise UserError(
                    _("%s has not any running loan request." % self.employee_id.name)
                )

    @api.onchange("loan_operation_type")
    def _onchange_loan_operation_type(self):
        if self.loan_operation_type:
            self.skip_reason = False
            self.loan_amount = False
            self.loan_payment_type = "fully"

    @api.model_create_multi
    def create(self, values):
        for val in values:
            if val.get("name", _("New")) == _("New"):
                if "company_id" in val:
                    val["name"] = self.env["ir.sequence"].with_context(
                        force_company=val["company_id"]
                    ).next_by_code("hr.loan.operation") or _("New")
                else:
                    val["name"] = self.env["ir.sequence"].next_by_code(
                        "hr.loan.operation"
                    ) or _("New")
        records = super(HrLoanOperation, self).create(values)
        for res in records:
            if res.employee_id and res.loan_id and res.effective_date:
                if (
                    res.loan_operation_type == "loan_payment"
                    and res.loan_payment_type == "partially"
                ):
                    if res.payment_amount >= res.loan_id.amount_to_pay:
                        raise UserError(
                            _("Payment amount should be less then loan amount to pay!")
                        )
        return records

    def write(self, values):
        for res in self:
            if (
                values.get("loan_operation_type") == "loan_payment"
                or values.get("loan_payment_type") == "partially"
                or values.get("payment_amount")
            ):
                if (
                    values.get("payment_amount")
                    and values.get("payment_amount") > res.loan_id.amount_to_pay
                ):
                    raise UserError(
                        _("Payment amount should be less then loan amount to pay!")
                    )
                if (
                    values.get("payment_amount")
                    and res.loan_payment_type == "partially"
                    and values.get("payment_amount") >= res.loan_id.amount_to_pay
                ):
                    raise UserError(
                        _(
                            "Payment amount should be less then loan amount to pay in partially payment!"
                        )
                    )
        return super(HrLoanOperation, self).write(values)

    def confirm_loan_operation(self):
        """
        sent the status of generating his/her loan operation in Confirm state
        """
        self.ensure_one()
        if self.loan_id.is_loan_freeze:
            raise UserError(_("Please Unfreeze Your Loan."))
        self.check_loan_operation_req(
            self.employee_id, self.effective_date, self.loan_operation_type
        )
        self.state = "confirm"

    def waiting_approval_loan_operation(self):
        """
        sent the status of generating his/her loan operation in Open state
        """
        self.ensure_one()
        self.state = "open"

    def approve_loan_operation(self):
        """
        sent the status of generating his/her loan operation in Approve state
        """
        self.ensure_one()
        self.approved_by = self.env.uid
        self.approved_date = datetime.today()
        timenow = time.strftime("%Y-%m-%d")
        for loan in self:
            if (
                loan.payment_type == "by_account"
                or loan.loan_operation_type == "increase_amount"
            ):
                amount = loan.loan_amount
                if loan.loan_operation_type == "loan_payment":
                    if loan.loan_payment_type == "fully":
                        amount = loan.loan_id.loan_amount
                    else:
                        amount = loan.payment_amount
                loan_name = "loan operation for %s" % loan.employee_id.name
                reference = "loan operation for %s" % loan.employee_id.name
                journal_id = loan.journal_id.id
                debit_account_id = loan.treasury_account_id.id
                credit_account_id = loan.emp_account_id.id

                debit_vals = {
                    "name": loan_name,
                    "partner_id": loan.employee_id.address_home_id.id,
                    "account_id": debit_account_id,
                    "journal_id": journal_id,
                    "date": timenow,
                    "debit": amount > 0.0 and amount or 0.0,
                    "credit": amount < 0.0 and -amount or 0.0,
                    "analytic_distribution": loan.analytic_distribution,
                }
                credit_vals = {
                    "name": loan_name,
                    "partner_id": loan.employee_id.address_home_id.id,
                    "account_id": credit_account_id,
                    "journal_id": journal_id,
                    "date": timenow,
                    "debit": amount < 0.0 and -amount or 0.0,
                    "credit": amount > 0.0 and amount or 0.0,
                    "analytic_distribution": loan.analytic_distribution,
                }
                vals = {
                    "name": "Loan For" + " " + loan_name + "-" + self.name,
                    "narration": loan_name,
                    "ref": reference,
                    "journal_id": journal_id,
                    "date": timenow,
                    "line_ids": [(0, 0, debit_vals), (0, 0, credit_vals)],
                }
                move = self.env["account.move"].create(vals)
                move._post()
                loan.move_id = move

            loan_line_id = False
            previous_ids = False
            remaining_ids = False
            if loan.effective_date:
                loan_line_id = loan.loan_id.loan_lines.filtered(
                    lambda l: not l.operation_id
                    and l.date
                    and l.date.month == loan.effective_date.month
                    and l.state in ["draft", "paid"]
                )
                previous_ids = loan.loan_id.loan_lines.filtered(
                    lambda l: not l.operation_id
                    and l.date
                    and l.date <= loan.effective_date
                    and l.state in ["draft", "paid"]
                )
                remaining_ids = loan.loan_id.loan_lines.filtered(
                    lambda l: not l.operation_id
                    and l.date
                    and l.date > loan.effective_date
                    and l.state in ["draft", "paid"]
                )

                if loan_line_id:
                    loan_line_id = loan_line_id[0]
                    loan_line_id.operation_id = loan.id
                if remaining_ids:
                    sorted_remaining_ids = sorted(remaining_ids, key=lambda l: l.id)
                    loan.loan_next_schedule_id = sorted_remaining_ids[0].id

            if loan.loan_operation_type == "loan_payment":
                loan_line_id = loan.loan_id.loan_lines.filtered(
                    lambda l: l.state in ["draft"]
                )
                previous_ids = loan.loan_id.loan_lines.filtered(
                    lambda l: l.state in ["draft"]
                )
                remaining_ids = loan.loan_id.loan_lines.filtered(
                    lambda l: l.state in ["draft"]
                )
                if loan_line_id:
                    loan_line_id = loan_line_id[0]
                    loan_line_id.operation_id = loan.id
                if remaining_ids:
                    sorted_remaining_ids = sorted(remaining_ids, key=lambda l: l.id)
                    loan.loan_next_schedule_id = sorted_remaining_ids[0].id

            if (
                loan.loan_operation_type == "loan_payment"
                and loan.loan_payment_type == "fully"
            ):
                if remaining_ids:
                    for rl_id in remaining_ids:
                        rl_id.state = "cancel"
                amount = loan.payment_amount
                amount = loan.loan_id.loan_amount - loan.loan_id.amount_paid
                slip_line_data = {
                    "loan_id": loan.loan_id.id,
                    "operation_id": loan.id,
                    "employee_id": loan.employee_id.id,
                    "date": fields.datetime.now(),
                    "amount": amount,
                }
                self.env["installment.line"].create(slip_line_data)
                loan.operation_applied = True
                loan.loan_id.state = "done"

            if not loan_line_id:
                raise UserError(
                    _(
                        "There is no any installment schedule are available or already another operation performed in the installment Schedule."
                    )
                )
            if loan.loan_operation_type == "skip_installment" and loan.effective_date:
                if loan_line_id:
                    last_id = sorted(
                        loan.loan_id.loan_lines, key=lambda k: k.id, reverse=True
                    )
                    if last_id:
                        last_id = last_id[0]
                        last_id.copy(
                            default={"date": last_id.date + relativedelta(months=1)}
                        )
                        last_id.amount = loan_line_id.amount
                    loan_line_id.state = "skip"
            elif (
                loan.loan_operation_type == "loan_payment"
                and previous_ids
                and remaining_ids
            ):  # and loan.effective_date
                amount = loan.loan_id.loan_amount
                if loan.loan_payment_type == "partially":
                    amount = loan.payment_amount
                if loan_line_id:
                    diff_amount = amount - loan_line_id.amount
                    # if len(previous_ids) == 1:
                    #     loan_line_id.amount = loan.loan_id.loan_amount
                    # else:
                    #     loan_line_id.amount = diff_amount
                    if loan.loan_payment_type == "partially" and remaining_ids:
                        previous_amount = sum(previous_ids.mapped("amount"))
                        remaining_diff = previous_amount - loan.payment_amount
                        remaining_dff_avg = remaining_diff / len(remaining_ids)
                        for rl_id in remaining_ids:
                            rl_id.amount = remaining_dff_avg
                        slip_line_data = {
                            "loan_id": loan.loan_id.id,
                            "operation_id": loan.id,
                            "employee_id": loan.employee_id.id,
                            "date": fields.datetime.now(),
                            "amount": loan.payment_amount,
                        }
                        self.env["installment.line"].create(slip_line_data)
                        loan.operation_applied = True
            elif (
                loan.loan_operation_type == "increase_amount"
                and loan.effective_date
                and loan.loan_amount
            ):
                amount_to_pay = loan.loan_id.amount_to_pay + loan.loan_amount
                loan_amount = loan.loan_amount + loan.loan_id.loan_amount
                loan.loan_id.write(
                    {"loan_amount": loan_amount, "amount_to_pay": amount_to_pay}
                )
                remaining_ids = loan.loan_id.loan_lines.filtered(
                    lambda l: l.date
                    and l.date >= loan.effective_date
                    and l.state in ["draft"]
                )
                if remaining_ids:
                    remaining_amount = sum(remaining_ids.mapped("amount"))
                    total_remaining_amount = loan.loan_amount + remaining_amount
                    avg_remaining_amount = total_remaining_amount / len(remaining_ids)
                    for rl_id in remaining_ids:
                        rl_id.amount = avg_remaining_amount
        self.state = "approve"

    def set_to_cancel(self):
        """
        sent the status of loan operation in cancel state
        """
        self.ensure_one()
        self.state = "cancel"

    def set_to_draft(self):
        """
        sent the status of loan operation in draft state
        """
        self.ensure_one()
        self.state = "draft"
        self.journal_id = False
        self.treasury_account_id = False
        self.emp_account_id = False
        self.analytic_distribution = {}
        self.operation_applied = False

    def refuse_loan_operation(self):
        """
        sent the status of generating his/her loan operation in Refuse state
        """
        self.ensure_one()
        self.refused_by = self.env.uid
        self.refused_date = datetime.today()
        self.state = "refuse"

    def unlink(self):
        """
        To remove the record, which is not in 'draft' and 'cancel' states
        """
        for rec in self:
            if rec.state not in ["draft", "cancel"]:
                raise ValidationError(
                    _(
                        "You cannot delete a request to Loan Operation which is in %s state."
                    )
                    % (rec.state)
                )
        return super(HrLoanOperation, self).unlink()
