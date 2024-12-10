# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class CashDeductionPaymentRegister(models.TransientModel):
    _name = "cash.deduction.register.payment"
    _description = "Deduction Cash Register Payment"

    #to getting default journal on Cash Decuction   
    def get_journal(self):
        context = self.env.context
        contract_deduction = self.env['contract.deduction'].browse(context.get('active_id'))
        if not contract_deduction.journal_id:
            raise UserError('Kindly define journal on Contract Deduction')
        return contract_deduction.journal_id.id

    amount = fields.Float(string="Amount")
    journal_id = fields.Many2one('account.journal', readonly=False, default=get_journal, domain="[('company_id', '=', company_id), ('type', 'in', ('bank', 'cash'))]")
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,
                                  compute='_compute_currency_id',
                                  help="The payment's currency.")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)
    payment_date = fields.Date(string="Payment Date", required=True,
                               default=fields.Date.context_today)
    communication = fields.Char(string="Memo", readonly=False)

    @api.depends('journal_id')
    def _compute_currency_id(self):
        for wizard in self:
            wizard.currency_id = wizard.journal_id.currency_id or wizard.company_id.currency_id

    def action_create(self):
        context = self.env.context
        deduction_id = self.env['contract.deduction'].browse(context.get('active_id'))
        per_installment_amount = 0
        remaining_installment_amount = 0
        for line in deduction_id.deduction_lines:
            if line.status == 'pending':
                remaining_installment_amount += line.amount
        if self.amount == 0 or self.amount < 0:
            raise UserError('Kindly add amount which is greater than zero')
        if remaining_installment_amount == 0:
            raise UserError('All installment are done')
        if self.amount > remaining_installment_amount:
            raise UserError('You are adding more than remaining amount, your remaining amount is %s' % remaining_installment_amount)
        if deduction_id.installment_type == 'installment_no':
            per_installment_amount = deduction_id.deduction_amount / deduction_id.installment
            if self.amount % per_installment_amount != 0:
                raise UserError('Kindly add amount in the sequence of per installment')
        elif deduction_id.installment_type == 'installment_amount':
            per_installment_amount = deduction_id.installment_amount
            if self.amount % per_installment_amount != 0:
                raise UserError('Kindly add amount in the sequence of per installment')
        limit = self.amount / per_installment_amount
        create_payment = self.env['account.payment'].create({
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id,
            'amount': self.amount,
            'date': self.payment_date,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': deduction_id.employee_id.address_home_id.id,
            'ref': self.communication,
        })
        created_payment_list = []
        for payment in deduction_id.payment_ids:
            created_payment_list.append(payment.id)
        created_payment_list.append(create_payment.id)
        deduction_id.update({'payment_ids': created_payment_list})
        deduction_line = self.env['contract.deduction.line'].search([('deduction_id','=',deduction_id.id),
                                                 ('status', '=', 'pending')],order='date asc', limit=limit)
        deduction_line.update({'status': 'done'})

