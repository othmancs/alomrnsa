# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import _, fields, models
from odoo.exceptions import UserError


class InsurancePremiumMultiInvoice(models.TransientModel):
    _name = "insurance.premium.multi.invoice"
    _description = "Insurance Premium Multi Invoice"

    start_date = fields.Date("From Date", required=True)
    end_date = fields.Date("To Date", required=True)

    def create_invoice_button(self):
        if self.start_date >= self.end_date:
            raise UserError(
                _("Error! premium start-date must be lower than premium end-date.")
            )
        context = dict(self._context or {})
        invoice_obj = self.env["account.move"]
        invoice_line_obj = self.env["account.move.line"]
        active_ids = context.get("active_ids", []) or []
        product_id = self.env.ref("saudi_hr_medical.insurance_prodcuct")
        insurance_premium = (
            self.env["insurance.premium"]
            .browse(active_ids)
            .filtered(
                lambda premium: premium.date >= self.start_date
                and premium.date <= self.end_date
                and premium.is_invoice_created == False
            )
        )
        invoice_dict = {}
        for premium in insurance_premium:
            if premium.supplier_id.id not in invoice_dict:
                contract = self.env["hr.contract"].search(
                    [
                        ("employee_id", "=", premium.insurance_id.employee_id.id),
                        ("state", "=", "open"),
                    ],
                    limit=1,
                )
                invoice_dict[premium.supplier_id.id] = {
                    "supplier": premium.supplier_id.id,
                    "invoice_origin": premium.insurance_id.name,
                    "account_id": premium.insurance_id.supplier_id.property_account_payable_id.id,
                    "invoice_line": {
                        "price_unit": premium.amount,
                    },
                    "premium_ids": [premium.id],
                    "branch_id": premium.insurance_id.branch_id.id,
                    "analytic_distribution": contract
                    and contract.analytic_distribution
                    or {},
                }
            else:
                invoice_dict[premium.supplier_id.id]["invoice_line"][
                    "price_unit"
                ] += premium.amount
                invoice_dict[premium.supplier_id.id]["premium_ids"].append(premium.id)
        for rec in invoice_dict.values():
            invoices_id = invoice_obj.create(
                {
                    "partner_id": rec["supplier"],
                    "type": "in_invoice",
                    "invoice_date": fields.Date.today(),
                    "ref": rec["invoice_origin"],
                    "invoice_date_due": fields.Date.today(),
                    "branch_id": rec["branch_id"],
                }
            )
            invoices_id._onchange_partner_id()
            # Create Invoice Lines
            line_default_fields = invoice_line_obj.fields_get()
            inv_line_val = invoice_line_obj.default_get(line_default_fields)
            inv_line_val.update(
                {
                    "name": product_id.name,
                    "product_id": product_id.id,
                    "price_unit": rec["invoice_line"]["price_unit"],
                    "quantity": 1.0,
                    "move_id": invoices_id.id,
                    "branch_id": rec["branch_id"],
                    "analytic_distribution": rec["analytic_distribution"],
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
                }
            )
            invoice_line_obj.with_context({"check_move_validity": False}).create(
                inv_line_val
            )
            invoices_id._compute_amount()
            move_container = {"records": invoices_id}
            invoices_id._check_balanced(move_container)
            invoices_id.with_context(
                {"check_move_validity": False}
            )._sync_dynamic_lines(move_container)

            premium_ids = insurance_premium.browse(rec["premium_ids"])
            premium_ids.write(
                {"invoice_id": invoices_id.id, "is_invoice_created": True}
            )
