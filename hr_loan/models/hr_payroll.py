# -*- coding: utf-8 -*-
import babel
import time
from datetime import datetime

from odoo import models, fields, api, tools, _


class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    loan_line_id = fields.Many2one('hr.loan.line', string="Loan Installment", help="Loan installment")
    desc = fields.Char("السبب")


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def compute_sheet(self):
        for payslip in self.filtered(lambda slip: slip.state not in ['cancel', 'done']):
            payslip.input_line_ids = payslip.get_inputs(payslip.date_from, payslip.date_to)
        return super().compute_sheet()

    def get_inputs(self, date_from, date_to):
        """This Compute the other inputs to employee payslip.
                           """
        res = []

        lon_obj = self.env['hr.loan'].search([('employee_id', '=', self.employee_id.id), ('state', '=', 'approve')])
        input_type = self.env['hr.payslip.input.type']
        for loan in lon_obj:
            total = 0.0
            for loan_line in loan.loan_lines:
                if date_from <= loan_line.date <= date_to and not loan_line.paid:
                    total += loan_line.amount
                    input_type_id = input_type.search([('code', '=', loan_line.loan_id.loan_type_id.rule_code)], limit=1)
                    if input_type_id:
                        vals = {
                            'input_type_id': input_type_id.id,
                            'name': loan_line.loan_id.loan_type_id.name,
                            'code': loan_line.loan_id.loan_type_id.rule_code,
                            'loan_line_id': loan_line.id,
                            'desc': loan_line.loan_id.reason,
                            'amount': total,
                        }
                        res.append((0, 0, vals))
        return res

    def action_payslip_done(self):
        for line in self.input_line_ids:
            if line.loan_line_id:
                line.loan_line_id.paid = True
                line.loan_line_id.loan_id._compute_loan_amount()
        return super(HrPayslip, self).action_payslip_done()

    # def _prepare_line_values(self, line, account_id, date, debit, credit):
    #     return {
    #         'name': line.name,
    #         'partner_id': line.employee_id.address_home_id.id,
    #         'account_id': account_id,
    #         'journal_id': line.slip_id.struct_id.journal_id.id,
    #         'date': date,
    #         'debit': debit,
    #         'credit': credit,
    #         # 'analytic_account_id': analytic,
    #         'analytic_account_id': line.salary_rule_id.analytic_account_id.id or line.slip_id.contract_id.analytic_account_id.id,
    #     }
