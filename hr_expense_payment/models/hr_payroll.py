# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, models, fields, tools, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pay_invoices_online = fields.Boolean(
        string="Pay Invoices Online",
        default=False,
        help="Enable online payments for invoices."
    )


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def action_payslip_done(self):
        """
            sent the status of generating record his/her payslip in 'done' state
        """
        res = super(HrPayslip, self).action_payslip_done()
        for payslip in self:
            expense_ids = self.get_expenses(payslip.employee_id, payslip.date_from, payslip.date_to)
            for expense in expense_ids:
                expense.slip_id = payslip.id
                expense.sheet_id.state = 'done'
        return res

    def get_expenses(self, employee_id, date_from, date_to):
        """
            Return expenses based on employee_id, date_from and date_to
        """
        expense_sheet_ids = self.env['hr.expense.sheet'].search([('employee_id', '=', employee_id.id),
                                                                 ('state', 'in', ['post', 'done'])])
        if expense_sheet_ids:
            expense_line_ids = self.env['hr.expense'].search([('sheet_id', 'in', expense_sheet_ids.ids)])
            if expense_line_ids:
                expense_ids = expense_line_ids.filtered(lambda expense: expense.include_salary and not expense.slip_id and expense.date >= date_from and expense.date <= date_to)
                return expense_ids
        return []

    def get_inputs(self, contracts, date_from, date_to):
        """
            Return input lines in payslip based on contracts, date_from and date_to
        """
        res = super(HrPayslip, self).get_inputs(contracts, date_from, date_to)
        rem_amt = ded_amt = 0.0
        for contract in contracts:
            expense_ids = self.get_expenses(contract.employee_id, date_from, date_to)
            for expense in expense_ids:
                if expense.payment_mode == 'own_account':
                    rem_amt += expense.total_amount
                elif expense.payment_mode == 'company_account' and expense.emp_contribution > 0.0:
                    ded_amt += expense.emp_contribution
            if rem_amt:
                res.append({
                    'name': 'Expense Reimburse',
                    'code': 'EXPENSEREM',
                    'amount': rem_amt,
                    'contract_id': contract.id,
                })
            if ded_amt:
                res.append({
                    'name': 'Expense Deduction',
                    'code': 'EXPENSE',
                    'amount': ded_amt,
                    'contract_id': contract.id,
                })
        return res
