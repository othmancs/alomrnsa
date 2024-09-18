# -*- coding: utf-8 -*-
# Part of odoo. See LICENSE file for full copyright and licensing details.

import time
from datetime import date, datetime

from dateutil import relativedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError

class HrContract(models.Model):
    _inherit = 'hr.contract'

    schedule_pay = fields.Many2one('schedule.pay', string='Schedule Pay', related='related_model.schedule_pay')
class SchedulePay(models.Model):
    _inherit = 'hr.contract'
    _name = 'schedule.pay'
    
    name = fields.Char(string='Name')

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def action_view_eos(self):
        context = dict(self.env.context) or {}
        action = self.env["ir.actions.actions"]._for_xml_id("saudi_hr_eos.eos_all")
        eos_ids = self.env["hr.employee.eos"].search([("employee_id", "=", self.id)])
        if eos_ids:
            action["domain"] = [("id", "in", eos_ids.ids)]
        else:
            action["views"] = [
                (self.env.ref("saudi_hr_eos.view_employee_eos_form").id, "form")
            ]
        context.update({"default_employee_id": self.id, "default_type": "resignation"})
        action["context"] = context
        return action

class SourceModel(models.Model):
    _name = 'source.model'
    
    register_ids = fields.One2many('hr.employee.eos', 'register_id', string="Registers")

class HrEmployeeEos(models.Model):
    _name = "hr.employee.eos"
    _inherit = ["mail.thread"]
    _description = "End of Service Indemnity (EOS)"

    register_id = fields.Many2one('source.model', string="Register")

    def some_method(self):
        # Search for the calendar
        calendar_records = self.env['resource.calendar'].search([('active', '=', True)])
        
        if not calendar_records:
            raise UserError("No active calendar records found.")
        elif len(calendar_records) > 1:
            raise UserError("More than one active calendar found. Please ensure only one is active.")

        calendar = calendar_records.ensure_one()

        # Proceed with the logic using the calendar
        _logger.info("Using calendar: %s", calendar.name)
        # Continue with the rest of the method logic

    def _get_currency(self):
        """
        return currency of current user
        """
        return self.env.user.company_id.currency_id.id

    def _calc_payable_eos(self):
        """
        Calculate the payable eos
        """
        for eos_amt in self:
            eos_amt.payable_eos = (
                eos_amt.total_eos
                + eos_amt.current_month_salary
                + eos_amt.others
                + eos_amt.annual_leave_amount
            ) or 0.0

    name = fields.Char(
        "Description",
        size=128,
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
    )
    eos_date = fields.Date(
        "Date",
        index=True,
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
        default=lambda self: datetime.today().date(),
    )
    employee_id = fields.Many2one(
        "hr.employee",
        "Employee",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
    )
    date_of_join = fields.Date(
        related="employee_id.date_of_join",
        type="date",
        string="Joining Date",
        store=True,
        readonly=True,
    )
    date_of_leave = fields.Date(
        related="employee_id.date_of_leave",
        type="date",
        string="Leaving Date",
        store=True,
        readonly=True,
    )
    duration_days = fields.Integer(
        "No of Days",
        readonly=True,
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
    )
    duration_months = fields.Integer(
        "No of Months",
        readonly=True,
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
    )
    duration_years = fields.Integer(
        "No. of Years",
        readonly=True,
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
    )
    type = fields.Selection(
        [
            ("resignation", "Resignation"),
            ("termination", "Termination"),
            ("death", "Death"),
        ],
        "Type",
        readonly=True,
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
    )
    calc_year = fields.Float(
        "Total Years", readonly=True, states={"draft": [("readonly", False)]}
    )
    payslip_id = fields.Many2one("hr.payslip", "Payslip", readonly=True)
    current_month_salary = fields.Float(
        "Salary of Current month",
        readonly=True,
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
    )
    others = fields.Float(
        "Others",
        readonly=True,
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
    )
    user_id = fields.Many2one(
        "res.users", "User", required=True, default=lambda self: self.env.uid
    )
    date_confirm = fields.Date(
        "Confirmation Date",
        index=True,
        copy=False,
        help="Date of the confirmation of the sheet expense. It's filled when the button Confirm is pressed.",
    )
    date_valid = fields.Date(
        "Validation Date",
        index=True,
        copy=False,
        help="Date of the acceptation of the sheet eos. It's filled when the button Validate is pressed.",
        readonly=True,
    )
    date_approve = fields.Date(
        "Approve Date",
        index=True,
        copy=False,
        help="Date of the Approval of the sheet eos. It's filled when the button Approve is pressed.",
        readonly=True,
    )
    user_valid = fields.Many2one(
        "res.users",
        "Validation by",
        copy=False,
        readonly=True,
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
        store=True,
    )
    user_approve = fields.Many2one(
        "res.users",
        "Approval by",
        copy=False,
        readonly=True,
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
        store=True,
    )
    note = fields.Text("Note")
    annual_leave_amount = fields.Float(
        "Leave Balance",
        readonly=True,
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
    )
    department_id = fields.Many2one("hr.department", "Department", readonly=True)
    job_id = fields.Many2one("hr.job", "Job", readonly=True)
    contract_id = fields.Many2one(
        "hr.contract",
        "Contract",
        readonly=True,
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
        default=lambda self: self.env.user.company_id,
    )
    state = fields.Selection(
        [
            ("draft", "New"),
            ("cancelled", "Refused"),
            ("confirm", "Waiting Approval"),
            ("validate", "Validated"),
            ("accepted", "Approved"),
            ("done", "Done"),
        ],
        "Status",
        readonly=True,
        tracking=True,
        default="draft",
        help="When the eos request is created the status is 'Draft'.\n It is confirmed by the user and request is sent to finance, the status is 'Waiting Confirmation'.\
        \nIf the finance accepts it, the status is 'Accepted'.",
    )
    total_eos = fields.Float(
        "Total Award", readonly=True, states={"draft": [("readonly", False)]}
    )
    payable_eos = fields.Float(compute=_calc_payable_eos, string="Total Amount")
    remaining_leave = fields.Float("Remaining Leave")

    # account
    journal_id = fields.Many2one(
        "account.journal",
        "Force Journal",
        help="The journal used when the eos is done.",
    )
    account_move_id = fields.Many2one("account.move", "Ledger Posting", copy=False)
    currency_id = fields.Many2one(
        "res.currency",
        "Currency",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
        default=_get_currency,
    )
    year_id = fields.Many2one(
        "year.year",
        "Year",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
        index=True,
        default=lambda self: self.env["year.year"].find(
            time.strftime("%Y-%m-%d"), True
        ),
        ondelete="cascade",
    )

    def _track_subtype(self, init_values):
        """
        Track Subtypes of EOS
        """
        self.ensure_one()
        if "state" in init_values and self.state == "draft":
            return self.env.ref("saudi_hr_eos.mt_employee_eos_new")
        elif "state" in init_values and self.state == "confirm":
            return self.env.ref("saudi_hr_eos.mt_employee_eos_confirm")
        elif "state" in init_values and self.state == "accepted":
            return self.env.ref("saudi_hr_eos.mt_employee_eos_accept")
        elif "state" in init_values and self.state == "validate":
            return self.env.ref("saudi_hr_eos.mt_employee_eos_validate")
        elif "state" in init_values and self.state == "done":
            return self.env.ref("saudi_hr_eos.mt_employee_eos_done")
        elif "state" in init_values and self.state == "cancelled":
            return self.env.ref("saudi_hr_eos.mt_employee_eos_cancel")
        return super(HrEmployeeEos, self)._track_subtype(init_values)

    @api.model_create_multi
    def create(self, values):
        """
        Create a new Record
        """
        for val in values:
            if val.get("employee_id"):
                eos_ids = self.env["hr.employee.eos"].search(
                    [("employee_id", "=", val.get("employee_id"))]
                )
                if eos_ids:
                    raise UserError(
                        _("%s's EOS is already Generated.") % (eos_ids.employee_id.name)
                    )
        return super(HrEmployeeEos, self).create(values)

    def write(self, values):
        """
        update existing record
        """
        if values.get("employee_id"):
            eos_ids = self.env["hr.employee.eos"].search(
                [("employee_id", "=", values.get("employee_id"))]
            )
            if eos_ids:
                raise UserError(
                    _("%s's EOS is already Generated.") % (eos_ids.employee_id.name)
                )
        return super(HrEmployeeEos, self).write(values)

    def unlink(self):
        """
        Remove record
        """
        for record in self:
            if record.state in ["confirm", "validate", "accepted", "done", "cancelled"]:
                raise UserError(
                    _("You cannot remove the record which is in %s state!")
                    % record.state
                )
        return super(HrEmployeeEos, self).unlink()

    @api.onchange("currency_id")
    def onchange_currency_id(self):
        """
        find the journal using currency
        """
        journal_ids = self.env["account.journal"].search(
            [
                ("type", "=", "purchase"),
                ("currency_id", "=", self.currency_id.id),
                ("company_id", "=", self.company_id.id),
            ],
            limit=1,
        )
        if journal_ids:
            self.journal_id = journal_ids.id

    def calc_eos(self):
        """
        Calculate eos
        """
        payslip_obj = self.env["hr.payslip"]
        for eos in self:
            if not eos.date_of_leave:
                raise UserError(_("Please define employee date of leaving!"))
            diff = relativedelta.relativedelta(eos.date_of_leave, eos.date_of_join)
            duration_days = diff.days
            duration_months = diff.months
            duration_years = diff.years
            eos.write(
                {
                    "duration_days": duration_days,
                    "duration_months": duration_months,
                    "duration_years": duration_years,
                }
            )
            selected_month = eos.date_of_leave.month
            selected_year = eos.date_of_leave.year
            date_from = date(selected_year, selected_month, 1)
            date_to = date_from + relativedelta.relativedelta(day=eos.date_of_leave.day)
            contract_ids = self.employee_id._get_contracts(
                date_from, date_to, states=["open"]
            )
            if not contract_ids:
                raise UserError(_("Please define contract for selected Employee!"))

            # Currently your company contract wage will be calculate as last salary.
            wages = contract_ids[0].wage
            total_eos = 0.0
            if 2 <= duration_years < 5:
                total_eos = (
                    ((wages / 2) * duration_years)
                    + (((wages / 2) / 12) * duration_months)
                    + ((((wages / 2) / 12) / 30) * duration_days)
                )
            elif 5 <= duration_years < 10:
                total_eos = (
                    ((wages / 2) * duration_years)
                    + ((wages / 12) * duration_months)
                    + (((wages / 12) / 30) * duration_days)
                )
            elif duration_years >= 10:
                total_eos = (
                    ((wages / 2) * 5)
                    + (wages * (duration_years - 5))
                    + ((wages / 12) * duration_months)
                    + ((wages / 365) * duration_days)
                )
            if not eos.journal_id:
                raise UserError(_("Please configure Journal before calculating EOS."))
            values = {
                "name": eos.employee_id.name,
                "employee_id": eos.employee_id.id or False,
                "date_from": date_from,
                "date_to": date_to,
                "contract_id": contract_ids[0].id,
                "journal_id": eos.journal_id.id,
            }
            if not eos.payslip_id:
                payslip_id = payslip_obj.create(values)
                eos.write({"payslip_id": payslip_id.id})
            eos.payslip_id.onchange_employee()
            eos.payslip_id.compute_sheet()
            net = 0.00
            payslip_line_obj = self.env["hr.payslip.line"]
            net_rule_id = payslip_line_obj.search(
                [("slip_id", "=", eos.payslip_id.id), ("code", "ilike", "NET")]
            )
            if net_rule_id:
                net_rule_obj = net_rule_id[0]
                net = net_rule_obj.total
            eos.write({"current_month_salary": net})
            payable_eos = total_eos
            if eos.type == "resignation":
                if 2 < eos.calc_year < 5:
                    payable_eos = total_eos / 3
                elif 5 < eos.calc_year < 10:
                    payable_eos = (total_eos * 2) / 3
                elif eos.calc_year > 10:
                    payable_eos = total_eos
            # Annual Leave Calc
            holiday_status_ids = self.env["hr.leave.type"].search(
                [("is_annual_leave", "=", True)], limit=1
            )
            if holiday_status_ids:
                leave_values = holiday_status_ids.get_days(
                    eos.employee_id.id
                )  # eos.year_id.id
                leaves_taken = leave_values[holiday_status_ids[0].id]["leaves_taken"]
                diff_date = relativedelta.relativedelta(
                    eos.date_of_leave, eos.year_id.date_start
                )

                allocate_leave_month = diff_date.months * eos.job_id.annual_leave_rate
                # remaining_leaves = allocate_leave_month - leaves_taken
                annual_leaving_id = self.env["annual.leaving"].search(
                    [("year_id", "=", eos.year_id.id)], limit=1
                )

                leave_details_id = self.env["leaves.details"].search(
                    [
                        ("annual_leaving_id", "=", annual_leaving_id.id),
                        ("employee_id", "=", eos.employee_id.id),
                    ]
                )
                remaining_leaves = leave_details_id.remaining_leaves
                # remaining_leaves = allocate_leave_month - leaves_taken

                annual_leave_amount = (wages / 30) * remaining_leaves
                eos.write(
                    {
                        "total_eos": payable_eos,
                        "annual_leave_amount": annual_leave_amount,
                        "remaining_leave": remaining_leaves,
                    }
                )
            return True

    @api.onchange("employee_id", "eos_date")
    def onchange_employee_id(self):
        """
        Calculate total no of year, month, days, etc depends on employee
        """
        for rec in self:
            if rec.employee_id:
                if not rec.employee_id.date_of_leave:
                    raise UserError(_("Please define employee date of leaving!"))
                if not rec.employee_id.date_of_join:
                    raise UserError(_("Please define employee date of join!"))
                selected_date = rec.employee_id.date_of_leave
                date_from = date(selected_date.year, selected_date.month, 1)
                date_to = date_from + relativedelta.relativedelta(day=selected_date.day)
                contract_ids = rec.employee_id._get_contracts(
                    date_from, date_to, states=["open"]
                )
                if not contract_ids:
                    raise UserError(_("Please define contract for selected Employee!"))
                calc_years = round(
                    (
                        (
                            rec.employee_id.date_of_leave - rec.employee_id.date_of_join
                        ).days
                        / 365.0
                    ),
                    2,
                )
                diff = relativedelta.relativedelta(
                    rec.employee_id.date_of_leave, rec.employee_id.date_of_join
                )
                rec.contract_id = contract_ids[0]
                rec.date_of_leave = rec.employee_id.date_of_leave
                rec.date_of_join = rec.employee_id.date_of_join
                rec.calc_year = calc_years
                rec.department_id = rec.employee_id.department_id.id or False
                rec.company_id = rec.employee_id.company_id.id or False
                rec.job_id = rec.employee_id.sudo().job_id.id or False
                rec.duration_years = diff.years or 0
                rec.duration_months = diff.months or 0
                rec.duration_days = diff.days or 0

    def mail_for_it_equipment(self):
        template_id = False
        try:
            template_id = self.env.ref("saudi_hr_eos.email_template_for_it_equipment")
        except ValueError:
            pass
        if template_id:
            hr_id = self.employee_id.hr_id or False
            if not hr_id:
                hr = self.env["ir.config_parameter"].sudo().get_param("saudi_hr.hr_id")
                hr_id = self.env["hr.employee"].browse(int(hr))
            if not hr_id:
                raise UserError(
                    _("Please configure HR in employee view or employee setting.")
                )
            template_id.with_context(hr_id=hr_id).send_mail(self.id, force_send=True)

    def eos_confirm(self):
        """
        EOS confirm state.
        """
        self.ensure_one()
        self.write({"state": "confirm", "date_confirm": time.strftime("%Y-%m-%d")})
        self.message_post(
            message_type="email",
            subtype_xmlid="mail.mt_comment",
            body=_("EOS Confirmed."),
        )

    def eos_validate(self):
        """
        EOS validate state.
        """
        self.ensure_one()
        finance_groups_config_obj = self.env["hr.groups.configuration"]
        for record in self:
            record.calc_eos()
            finance_groups_config_ids = finance_groups_config_obj.search(
                [
                    ("branch_id", "=", record.employee_id.branch_id.id or False),
                    ("finance_ids", "!=", False),
                ]
            )
            partner_ids = (
                finance_groups_config_ids
                and [
                    item.user_id.partner_id.id
                    for item in finance_groups_config_ids.finance_ids
                    if item.user_id
                ]
                or []
            )
            if record.employee_id.parent_id.user_id:
                partner_ids.append(record.employee_id.parent_id.user_id.partner_id.id)
            record.message_subscribe(partner_ids=partner_ids)
        self.write(
            {
                "state": "validate",
                "date_valid": time.strftime("%Y-%m-%d"),
                "user_valid": self.env.uid,
            }
        )
        self.message_post(
            message_type="email",
            subtype_xmlid="mail.mt_comment",
            body=_("EOS Validated."),
        )
        self.mail_for_it_equipment()

    def eos_accept(self):
        """
        EOS accept state
        """
        self.ensure_one()
        self.write(
            {
                "state": "accepted",
                "date_approve": time.strftime("%Y-%m-%d"),
                "user_approve": self.env.uid,
            }
        )
        self.message_post(
            message_type="email",
            subtype_xmlid="mail.mt_comment",
            body=_("EOS Approved."),
        )

    def eos_cancelled(self):
        """
        EOS confirm state
        """
        self.ensure_one()
        self.state = "cancelled"
        self.message_post(
            message_type="email",
            subtype_xmlid="mail.mt_comment",
            body=_("EOS Cancelled."),
        )

    def eos_draft(self):
        """
        EOS set to draft state
        """
        self.ensure_one()
        self.state = "draft"
        self.message_post(
            message_type="email", subtype_xmlid="mail.mt_comment", body=_("EOS Draft.")
        )

    def action_receipt_create(self):
        """
        Main function that is called when trying to create the accounting entries related to an expense
        """
        for eos in self:
            if not eos.employee_id.address_home_id:
                raise UserError(_("The employee must have a home address."))
            if not eos.employee_id.address_home_id.property_account_payable_id.id:
                raise UserError(
                    _(
                        "The employee must have a payable account set on his home address."
                    )
                )
            if not eos.journal_id:
                raise UserError(_("Please configure employee EOS for journal."))
            timenow = time.strftime("%Y-%m-%d")
            amount = 0.0
            amount -= eos.payable_eos
            eos_name = eos.name.split("\n")[0][:64]
            reference = eos.name
            journal_id = eos.journal_id.id
            debit_account_id = eos.journal_id.default_account_id.id
            credit_account_id = (
                eos.employee_id.address_home_id.property_account_payable_id.id
            )
            if not debit_account_id:
                raise UserError(
                    _("Please configure %s journal's expense account.")
                    % eos.journal_id.name
                )
            debit_vals = {
                "name": eos_name,
                "account_id": debit_account_id,
                "journal_id": journal_id,
                "partner_id": eos.employee_id.address_home_id.id,
                "date": timenow,
                "debit": amount > 0.0 and amount or 0.0,
                "credit": amount < 0.0 and -amount or 0.0,
                "analytic_distribution": eos.contract_id.analytic_distribution or {},
            }
            credit_vals = {
                "name": eos_name,
                "account_id": credit_account_id,
                "partner_id": eos.employee_id.address_home_id.id,
                "journal_id": journal_id,
                "date": timenow,
                "debit": amount < 0.0 and -amount or 0.0,
                "credit": amount > 0.0 and amount or 0.0,
                "analytic_distribution": eos.contract_id.analytic_distribution or {},
            }
            vals = {
                "name": "/",
                "narration": eos_name,
                "ref": reference,
                "journal_id": journal_id,
                "date": timenow,
                "line_ids": [(0, 0, debit_vals), (0, 0, credit_vals)],
            }
            move = self.env["account.move"].create(vals)
            move.action_post()
            self.write({"account_move_id": move.id, "state": "done"})

    def action_view_receipt(self):
        """
        This function returns an action that display existing account.move of given expense ids.
        """
        assert (
            len(self.ids) == 1
        ), "This option should only be used for a single id at a time"
        self.ensure_one()
        assert self.account_move_id
        try:
            dummy, view_id = self.env["ir.model.data"]._xmlid_lookup(
                "account.view_move_form"
            )
        except ValueError:
            view_id = False
        result = {
            "name": _("EOS Account Move"),
            "view_mode": "form",
            "view_id": view_id,
            "res_model": "account.move",
            "type": "ir.actions.act_window",
            "nodestroy": True,
            "target": "current",
            "res_id": self.account_move_id.id,
        }
        return result


class HrJob(models.Model):
    _inherit = "hr.job"
    _description = "HR Job"

    annual_leave_rate = fields.Float("Annual Leave Rate", default=2)
