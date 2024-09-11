# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AdvanceSalaryPayment(models.TransientModel):
    _name = "advance.salary.payment"
    _description = "Advance Salary Payment"

    amount = fields.Monetary(string='Payment Amount', readonly=True)
    journal_id = fields.Many2one('account.journal', string='Payment Method', required=True)
    account_id = fields.Many2one('account.account', 'Expense Account', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.today(), required=True, copy=False)
    advance_salary_id = fields.Many2one('hr.advance.salary', string='Advance Salary')

    @api.model
    def default_get(self, fields):
        rec = super(AdvanceSalaryPayment, self).default_get(fields)
        if rec.get('advance_salary_id'):
            advance_salary_id = self.env['hr.advance.salary'].browse(rec.get('advance_salary_id'))
            rec['amount'] = advance_salary_id.request_amount
        return rec

    def action_validate_payment(self):
        self.ensure_one()
        debit_account = self.account_id.id
        credit_account = self.journal_id.company_id.account_journal_payment_credit_account_id.id
        contract_id = self.env['hr.contract'].search([('employee_id', '=', self.advance_salary_id.employee_id.id),
                                                    ('state', '=', 'open')], limit=1)
        analytic_account = contract_id and contract_id.analytic_account_id.id or False
        analytic_distribution = contract_id and contract_id.analytic_distribution or False
        move_vals = {'move_type': 'entry',
                 'ref': self.advance_salary_id.name,
                 'journal_id': self.journal_id.id,
                 'date': self.payment_date,
                 #'branch_id': self.advance_salary_id.employee_id.branch_id.id,
                 'company_id': self.advance_salary_id.company_id.id,
                 'line_ids': [(0, 0, {'account_id': credit_account,
                                    'credit': self.amount,
                                    'name': self.advance_salary_id.name + 'Payment' or '',
                                    'partner_id': self.advance_salary_id.employee_id.address_home_id.id,
                                    #'branch_id': self.advance_salary_id.employee_id.branch_id.id,
                                    # 'analytic_account_id': analytic_account or False,
                                    'analytic_distribution': analytic_distribution,
                                    }),
                            (0, 0, {'account_id': debit_account,
                                    'debit': self.amount,
                                    'name': self.advance_salary_id.name or '',
                                    'partner_id': self.advance_salary_id.employee_id.address_home_id.id,
                                    #'branch_id': self.advance_salary_id.employee_id.branch_id.id,
                                    # 'analytic_account_id': analytic_account or False,
                                    'analytic_distribution': analytic_distribution,
                                    })
                            ]
                 }
        move_id = self.env['account.move'].create(move_vals)
        move_id.action_post()

        self.advance_salary_id.write({'state': 'paid',
                                    'paid_date': self.payment_date,
                                    'paid_by': self.env.uid,
                                    'payment_entry_id': move_id.id,
                                    'paid_amount': self.amount})

        action = self.env["ir.actions.actions"]._for_xml_id('account.action_move_journal_line')
        action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
        action['res_id'] = move_id.id
        return action
