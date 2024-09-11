# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    pen_reg_ids = fields.Many2many(
        "hr.penalty.register",
        "payslip_punishment_rel",
        "payslip_id",
        "punishment_id",
        string="Penalty",
    )

    def compute_sheet(self):
        res = super(HrPayslip, self).compute_sheet()
        for payslip in self:
            slip_line_ids = self.env["hr.payslip.line"].search(
                [("slip_id", "=", payslip.id), ("code", "=", "PEN")]
            )
            if slip_line_ids:
                slip_line_ids.unlink()

            pen_ids = self.env["hr.penalty.register"].search(
                [
                    ("employee_id", "=", payslip.employee_id.id),
                    ("state", "=", "done"),
                    ("is_ded", "=", True),
                    ("pen_date", ">=", payslip.date_from),
                    ("pen_date", "<=", payslip.date_to),
                ]
            )
            self.pen_reg_ids = [(4, pen_reg.id) for pen_reg in pen_ids]

            rule_ids = self.env["hr.salary.rule"].search([("code", "=", "PEN")])
            d_amt = sum(pen_reg.deduction_amt for pen_reg in pen_ids)
            if rule_ids and d_amt:
                rule = rule_ids[0]
                slip_line_data = {
                    "slip_id": payslip.id,
                    "salary_rule_id": rule.id,
                    "contract_id": payslip.contract_id.id,
                    "name": rule.name,
                    "code": "PEN",
                    "category_id": rule.category_id.id,
                    "sequence": rule.sequence,
                    "appears_on_payslip": rule.appears_on_payslip,
                    "condition_select": rule.condition_select,
                    "condition_python": rule.condition_python,
                    "condition_range": rule.condition_range,
                    "condition_range_min": rule.condition_range_min,
                    "condition_range_max": rule.condition_range_max,
                    "amount_select": rule.amount_select,
                    "amount_fix": rule.amount_fix,
                    "amount_python_compute": rule.amount_python_compute,
                    "amount_percentage": rule.amount_percentage,
                    "amount_percentage_base": rule.amount_percentage_base,
                    "register_id": rule.register_id.id,
                    "amount": -d_amt,
                    "employee_id": payslip.employee_id.id,
                }
                self.env["hr.payslip.line"].create(slip_line_data)
                pen_ids.write({"payslip_id": self.id})

                net_ids = self.env["hr.payslip.line"].search(
                    [("slip_id", "=", payslip.id), ("code", "=", "NET")]
                )
                if net_ids:
                    net_record = net_ids[0]
                    net_ids.write({"amount": net_record.amount - d_amt})
        return res
