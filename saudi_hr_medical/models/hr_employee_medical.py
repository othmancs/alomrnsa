# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from datetime import timedelta

from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class HrEmployee(models.Model):
    _inherit = "hr.employee"
    _order = "id desc"

    insurance_ids = fields.One2many(
        "insurance.details", "employee_id", string="Medical Insurance"
    )


class EmployeeClass(models.Model):
    _name = "employee.class"
    _description = "Employee Class"

    name = fields.Char("Name", required=True)


class InsuranceDetails(models.Model):
    _name = "insurance.details"
    _inherit = "mail.thread"
    _order = "id desc"
    _description = "Employee Medical Insurance"

    @api.depends("employee_id")
    def _get_employee_vals(self):
        """
        Set value dob, gender, company_id, currency_id, member_name depends on employee_id
        """
        for insurance in self:
            if insurance.employee_id:
                insurance.dob = insurance.employee_id.sudo().birthday
                insurance.gender = insurance.employee_id.sudo().gender
                insurance.company_id = (
                    insurance.employee_id.company_id
                    and insurance.employee_id.company_id.id
                    or False
                ) or (
                    insurance.env.user.company_id
                    and insurance.env.user.company_id.id
                    or False
                )
                insurance.currency_id = (
                    insurance.company_id
                    and insurance.company_id.currency_id
                    and insurance.company_id.currency_id.id
                    or False
                )
                insurance.member_name = insurance.employee_id.name

    def _add_followers(self):
        """
        Add employee and Responsible user in followers
        """
        for insurance in self:
            partner_ids = []
            if insurance.employee_id.user_id:
                partner_ids.append(insurance.employee_id.user_id.partner_id.id)
            if insurance.responsible_id:
                partner_ids.append(insurance.responsible_id.partner_id.id)
            insurance.message_subscribe(partner_ids=partner_ids)

    def _count_claim(self):
        """
        Count the number of claims
        """
        for insurance in self:
            insurance.claim_count = len(insurance.claims_ids)

    name = fields.Char(string="Insurance Number", readonly=True, tracking=True)
    card_code = fields.Char("Card Code", required=True, tracking=True)
    member_name = fields.Char("Member Name", compute=_get_employee_vals, store=True)
    note = fields.Text("Note")
    claim_count = fields.Integer(string="# of claims", compute=_count_claim)
    insurance_amount = fields.Float("Insurance Amount", required=True, tracking=True)
    premium_amount = fields.Float("Premium Amount", required=True, tracking=True)
    start_date = fields.Date(
        "Start Date", required=True, default=fields.Date.today(), tracking=True
    )
    end_date = fields.Date("End Date", required=True, tracking=True)
    dob = fields.Date("Date of Birth", compute=_get_employee_vals, store=True)
    premium_type = fields.Selection(
        [
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("half", "Half Yearly"),
            ("yearly", "Yearly"),
        ],
        string="Payment Mode",
        required=True,
        default="monthly",
        tracking=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirm"),
            ("cancelled", "Cancel"),
            ("done", "Done"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    class_id = fields.Many2one("employee.class", string="Class", tracking=True)
    gender = fields.Selection(
        [("male", "Male"), ("female", "Female")], compute=_get_employee_vals, store=True
    )
    relation = fields.Selection(
        [("employee", "Employee"), ("child", "Child"), ("spouse", "Spouse")],
        tracking=True,
    )
    employee_id = fields.Many2one(
        "hr.employee", required=True, string="Employee", tracking=True
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
    supplier_id = fields.Many2one(
        "res.partner", required=True, string="Supplier", tracking=True
    )
    currency_id = fields.Many2one(
        "res.currency", compute=_get_employee_vals, store=True
    )
    responsible_id = fields.Many2one(
        "res.users",
        string="Responsible",
        required=True,
        default=lambda self: self.env.uid,
        tracking=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        compute=_get_employee_vals,
        store=True,
        tracking=True,
    )
    claims_ids = fields.One2many("claim.details", "insurance_id", string="Claims")
    premium_ids = fields.One2many(
        "insurance.premium", "insurance_id", string="Insurance premium"
    )
    total_paid_premium = fields.Float(
        "Total Paid Premium", compute="_compute_total_paid_premium"
    )

    _sql_constraints = [
        (
            "card_code_uniq",
            "unique(card_code)",
            "The card code of the insurance must be unique!",
        ),
    ]

    @api.constrains("insurance_amount", "premium_amount")
    def check_premium_amount(self):
        """
        Check premium amount is less than insurance amount or not
        """
        for insurance in self:
            if insurance.insurance_amount < insurance.premium_amount:
                raise ValidationError(
                    _("Insurance amount must be greater then premium amount!")
                )

    @api.depends("premium_ids")
    def _compute_total_paid_premium(self):
        for rec in self:
            rec.total_paid_premium = sum(
                rec.premium_ids.search(
                    [
                        ("is_invoice_created", "=", True),
                        ("id", "in", rec.premium_ids.ids),
                    ]
                ).mapped("amount")
            )

    @api.model_create_multi
    def create(self, values):
        """
        Create a new record and employee add in followers
        """
        for val in values:
            val["name"] = self.env["ir.sequence"].next_by_code("insurance.details")
        return super(InsuranceDetails, self).create(values)

    @api.onchange("company_id")
    def onchange_company_id(self):
        """
        Set currency: Value from Company
        """
        self.currency_id = False
        if self.company_id:
            self.currency_id = (
                self.company_id.currency_id and self.company_id.currency_id.id or False
            )

    def action_generate_premiums(self):
        """
        Generate insurance premiums
        """
        self.premium_ids = []
        if self.start_date and self.end_date and self.premium_type:
            premium_list = []
            next_date = self.start_date
            index = 1
            while next_date <= self.end_date:
                premium_list.append(
                    {
                        "sequence": index,
                        "date": next_date,
                        "amount": self.premium_amount or 0.0,
                        "is_invoice_created": False,
                    }
                )

                if self.premium_type == "monthly":
                    next_date = next_date + relativedelta(months=1)
                elif self.premium_type == "quarterly":
                    next_date = next_date + relativedelta(months=3)
                elif self.premium_type == "half":
                    next_date = next_date + relativedelta(months=6)
                else:
                    next_date = next_date + relativedelta(months=12)
                index += 1
            final_list = [(0, 0, line) for line in premium_list]
            self.premium_ids = final_list

    def action_cancelled(self):
        """
        Set insurance status as 'cancelled'
        """
        self.ensure_one()
        self.state = "cancelled"

    def action_confirm(self):
        """
        Set insurance status as 'confirmed'
        """
        self.ensure_one()
        self._add_followers()
        if self.insurance_amount <= 0 or self.premium_amount <= 0:
            raise UserError(
                _("Please enter proper value for Insurance Amount and Premium Amount")
            )
        self.action_generate_premiums()
        self.state = "confirmed"

    def action_done(self):
        """
        Set insurance status as 'done'
        """
        self.ensure_one()
        self.state = "done"

    def action_set_to_draft(self):
        """
        Set insurance status as 'draft'
        """
        self.ensure_one()
        self.state = "draft"

    def view_insurance(self):
        """
        Redirect On Employee Insurance Form
        """
        self.ensure_one()
        form_view = self.env.ref("saudi_hr_medical.insurance_details_form_view")
        return {
            "type": "ir.actions.act_window",
            "name": _("Insurance"),
            "res_model": "insurance.details",
            "view_mode": "from",
            "views": [(form_view.id, "form")],
            "res_id": self.id,
            "context": self.env.context,
            "create": False,
            "editable": False,
        }

    def view_claims(self):
        """
        Redirect On Insurance Claim
        """
        self.ensure_one()
        if self.claims_ids:
            tree_view = self.env.ref("saudi_hr_medical.claims_details_tree_view")
            form_view = self.env.ref("saudi_hr_medical.claim_details_form_view")
            return {
                "type": "ir.actions.act_window",
                "name": _("Claims"),
                "res_model": "claim.details",
                "view_mode": "form",
                "views": [(tree_view.id, "tree"), (form_view.id, "form")],
                "domain": [("id", "in", self.claims_ids.ids)],
                "context": self.env.context,
            }

    @api.model
    def check_insurance_expiry(self):
        """
        Send mail for Insurance Expiry
        """
        try:
            template_id = self.env.ref(
                "saudi_hr_medical.hr_medical_insurance_expiration_email"
            )
        except ValueError:
            template_id = False
        for insurance in self.search([("state", "=", "confirmed")]):
            reminder_date = insurance.end_date - timedelta(days=10)
            if reminder_date == fields.Date.today() and template_id:
                template_id.send_mail(
                    insurance.id, force_send=True, raise_exception=True
                )


class InsurancePremium(models.Model):
    _name = "insurance.premium"
    _description = "Insurance Premium"

    sequence = fields.Integer("Sequence", required=True)
    date = fields.Date("Premium Date", required=True)
    amount = fields.Float("Premium Amount", required=True)
    is_invoice_created = fields.Boolean("Invoice Created")
    insurance_id = fields.Many2one("insurance.details", string="Insurance")
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", related="insurance_id.employee_id", store=True
    )
    branch_id = fields.Many2one(
        "hr.branch", string="Office", related="employee_id.branch_id", store=True
    )
    department_id = fields.Many2one(
        "hr.department",
        string="Department",
        related="employee_id.department_id",
        store=True,
    )
    invoice_id = fields.Many2one("account.move", string="Invoice")
    supplier_id = fields.Many2one(
        "res.partner", string="Supplier", related="insurance_id.supplier_id", store=True
    )

    def create_invoice(self):
        """
        Create Invoice for Premium Amount
        """
        product_id = self.env.ref("saudi_hr_medical.insurance_prodcuct")
        account_move_obj = self.env["account.move"]
        account_move_line_obj = self.env["account.move.line"]
        if not self.insurance_id.supplier_id.property_account_payable_id:
            raise UserError(
                _('There is no payable account defined for this supplier: "%s".')
                % (self.insurance_id.supplier_id.name,)
            )
        contract = self.env["hr.contract"].search(
            [
                ("employee_id", "=", self.insurance_id.employee_id.id),
                ("state", "=", "open"),
            ],
            limit=1,
        )
        inv_default = {}
        inv_default.update(
            {
                "partner_id": self.insurance_id.supplier_id.id,
                "invoice_date": self.date,
                "move_type": "in_invoice",
                "ref": self.insurance_id.name,
                "invoice_date_due": self.date,
            }
        )
        invoices_id = account_move_obj.create(inv_default)
        account_move_line_obj.with_context({"check_move_validity": False}).create(
            {
                "name": "Insurance Premium",
                "price_unit": self.amount,
                "quantity": 1.0,
                "product_id": product_id.id,
                "account_id": (
                    product_id.property_account_expense_id
                    and product_id.property_account_expense_id.id
                    or False
                )
                or (
                    product_id.categ_id.property_account_expense_categ_id
                    and product_id.categ_id.property_account_expense_categ_id.id
                    or False
                ),
                "move_id": invoices_id.id,
                "analytic_distribution": contract.analytic_distribution or {},
            }
        )
        invoices_id._compute_amount()
        move_container = {"records": invoices_id}
        invoices_id._check_balanced(move_container)
        invoices_id.with_context({"check_move_validity": False})._sync_dynamic_lines(
            move_container
        )
        self.invoice_id = invoices_id and invoices_id.id or False
        self.is_invoice_created = True

    def view_invoice_action(self):
        """
        View Invoice
        """
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "account.move",
            "views": [(self.env.ref("account.view_move_form").id, "form")],
            "res_id": self.invoice_id.id,
        }

    def print_invoice(self):
        """
        Print Invoice
        """
        return self.env.ref("account.account_invoices").report_action(self.invoice_id)

    def action_invoice_create(self):
        """
        Create Invoice for Premium Amount
        """
        premiums = self.search(
            [
                ("insurance_id.state", "=", "confirmed"),
                ("is_invoice_created", "=", False),
                ("date", "=", fields.date.today()),
            ]
        )
        for premium in premiums:
            premium.create_invoice()


class ClaimDetails(models.Model):
    _name = "claim.details"
    _description = "Claim Details"
    _inherit = "mail.thread"

    @api.depends("insurance_id", "responsible_id")
    def _set_insurance_vals(self):
        """
        Set claim company id and currency id
        """
        for claim in self:
            claim.company_id = claim.env.user.company_id.id
            claim.currency_id = claim.company_id.currency_id.id
            if claim.insurance_id:
                claim.company_id = claim.insurance_id.company_id.id
                claim.currency_id = claim.company_id.currency_id.id

    name = fields.Char(string="Claim Number", readonly=True)
    date_applied = fields.Date(
        "Date Applied", default=fields.Date.today(), required=True, tracking=True
    )
    claim_amount = fields.Float("Claim Amount", required=True, tracking=True)
    passed_amount = fields.Float("Passed Amount", tracking=True)
    insurance_id = fields.Many2one(
        "insurance.details",
        string="Insurance",
        required=True,
        domain="[('state', '=', 'confirmed'), ('employee_id', '=', employee_id)]",
        tracking=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        compute=_set_insurance_vals,
        store=True,
        tracking=True,
    )
    responsible_id = fields.Many2one(
        "res.users",
        string="Responsible",
        required=True,
        default=lambda self: self.env.uid,
        tracking=True,
    )
    currency_id = fields.Many2one(
        "res.currency", compute=_set_insurance_vals, store=True
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirm", "Confirmed"),
            ("refuse", "Refused"),
            ("cancel", "Cancelled"),
            ("done", "Done"),
        ],
        default="draft",
        tracking=True,
    )
    note = fields.Text("Note")
    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=True,
        default=lambda self: self.env["hr.employee"].get_employee(),
    )
    is_hr_user = fields.Boolean(
        compute="_check_hr_user",
        help="To check the current user is Hr/User or Hr/Manager",
    )

    def _check_hr_user(self):
        for rec in self:
            rec.is_hr_user = self.env.user.has_group(
                "hr.group_hr_user"
            ) or self.env.user.has_group("hr.group_hr_manager")

    def _add_followers(self):
        """
        Add employee and Responsible user in followers
        """
        for claim in self:
            partner_ids = []
            if claim.employee_id.user_id:
                partner_ids.append(claim.employee_id.user_id.partner_id.id)
            if claim.responsible_id:
                partner_ids.append(claim.responsible_id.partner_id.id)
            claim.message_subscribe(partner_ids=partner_ids)

    @api.model_create_multi
    def create(self, values):
        """
        Create a new record and employee add in followers
        """
        for val in values:
            val["name"] = self.env["ir.sequence"].next_by_code("claim.details")
        return super(ClaimDetails, self).create(values)

    @api.onchange("insurance_id")
    def onchange_insurance_id(self):
        """
        Set Responsible: Value from Insurance
        """
        self.responsible_id = False
        if self.insurance_id:
            self.responsible_id = (
                self.insurance_id.responsible_id
                and self.insurance_id.responsible_id
                or False
            )

    @api.onchange("company_id")
    def onchange_company_id(self):
        """
        Set Currency: Value from Company
        """
        self.currency_id = False
        if self.company_id:
            self.currency_id = (
                self.company_id.sudo().currency_id
                and self.company_id.currency_id.id
                or False
            )

    def action_confirm(self):
        """
        Set claim status as 'confirm'
        """
        self.ensure_one()
        if self.claim_amount <= 0:
            raise UserError(_("Please enter proper value for Claim Amount"))
        self._add_followers()
        self.state = "confirm"

    def action_refuse(self):
        """
        Set claim status as 'refuse'
        """
        self.ensure_one()
        self.state = "refuse"

    def action_cancel(self):
        """
        Set claim status as 'cancel'
        """
        self.ensure_one()
        self.state = "cancel"

    def action_done(self):
        """
        Set claim status as 'done'
        """
        self.ensure_one()
        if self.passed_amount <= 0:
            raise UserError(_("Passed Amount should be greater then 0"))
        else:
            self.state = "done"

    def action_set_to_draft(self):
        """
        Set claim status as 'draft'
        """
        self.ensure_one()
        self.state = "draft"
