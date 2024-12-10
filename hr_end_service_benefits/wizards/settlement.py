# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from datetime import datetime, date, timedelta
from odoo import models, fields, api, exceptions, _
import math
import logging

_logger = logging.getLogger(__name__)


class Settlement(models.TransientModel):
    _name = 'hr.benefit.settlement'

    def _default_debit_account_id(self):
        return self.env.user.company_id.debit_account_id

    def _default_expense_account_id(self):
        return self.env.user.company_id.expense_account_id

    def _default_expense_journal_id(self):
        return self.env.user.company_id.expense_journal_id

    def _default_settlement_journal_id(self):
        return self.env.user.company_id.settlement_journal_id

    request_id = fields.Many2one(comodel_name="hr.end.service.benefit")
    employee_id = fields.Many2one(comodel_name="hr.employee", related='request_id.employee_id')
    amount = fields.Float(related='request_id.amount')
    total_payslip_deserved_amount = fields.Float(related='request_id.total_payslip_deserved_amount')
    settlement_journal_id = fields.Many2one(comodel_name="account.journal", default=_default_settlement_journal_id)
    payment_date = fields.Date(string=" Payment Date", default=datetime.now().strftime('%Y-%m-%d'), )
    expense_account_id = fields.Many2one(comodel_name="account.account", default=_default_expense_account_id)
    expense_journal_id = fields.Many2one(comodel_name="account.journal", default=_default_expense_journal_id, )
    expense_date = fields.Date(string="Expense Date", default=datetime.now().strftime('%Y-%m-%d'), )

    def settle_employee_reward(self):
        for record in self:
            if not record.employee_id.address_home_id:
                raise exceptions.ValidationError(
                    _("This employee has no private address,"
                      " please add it at employee profile !!"))
            # if not record.employee_id.address_home_id:
            #     raise exceptions.ValidationError(
            #         _("This employee private address is not a supplier, please mark it as a supplier!!"))
            if not record.employee_id.address_home_id.property_account_payable_id:
                raise exceptions.ValidationError(
                    _("This employee has no payable account at private address,"
                      " please add it at employee private address partner !!"))
            # Journal Entry Creation
            line_ids = []
            name = _('Ending service reward settlement of %s') % (record.employee_id.name)
            move_dict = {
                'narration': name,
                'ref': name,
                'journal_id': record.expense_journal_id.id,
                'date': record.expense_date,
            }
            amount = record.amount
            total_payslip_deserved_amount = record.total_payslip_deserved_amount
            debit_account_id = record.expense_account_id.id
            credit_account_id = record.employee_id.address_home_id.property_account_payable_id.id
            if debit_account_id and record.employee_id.address_home_id:
                debit_line = (0, 0, {
                    'name': name + str(' debit line'),
                    'partner_id': record.employee_id.address_home_id.id,
                    'account_id': debit_account_id,
                    'journal_id': record.expense_journal_id.id,
                    'date': record.expense_date,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                })
                line_ids.append(debit_line)
            if credit_account_id:
                credit_line = (0, 0, {
                    'name': name + str(' credit line'),
                    'partner_id': record.employee_id.address_home_id.id,
                    'account_id': credit_account_id,
                    'journal_id': record.expense_journal_id.id,
                    'date': record.expense_date,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                })
                line_ids.append(credit_line)
            move_dict['line_ids'] = line_ids
            move = self.env['account.move'].with_context(check_move_validity=False).create([move_dict])
            move.action_post()

            # Payment Creation
            name = _('Ending service reward payment of %s') % (record.employee_id.name)
            payment_dict = {
                # 'communication': name,
                'reward_id': record.request_id.id,
                'payment_type': 'outbound',
                'partner_type': 'supplier',
                'amount': record.amount,
                'journal_id': record.settlement_journal_id.id,
                'partner_id': record.employee_id.address_home_id.id,
                'payment_method_line_id': record.settlement_journal_id.outbound_payment_method_line_ids[0].id,
                'date': record.payment_date,
            }
            payment_id = self.env['account.payment'].create(payment_dict)
            payment_id.action_post()
            if record.total_payslip_deserved_amount > 0:
                payslip_name = _('Ending service payslip payment of %s') % (record.employee_id.name)
                payslip_payment_dict = {
                    # 'communication': name,
                    'reward_id': record.request_id.id,
                    'payment_type': 'outbound',
                    'partner_type': 'supplier',
                    'amount': record.total_payslip_deserved_amount,
                    'journal_id': record.settlement_journal_id.id,
                    'partner_id': record.employee_id.address_home_id.id,
                    'payment_method_line_id': record.settlement_journal_id.outbound_payment_method_line_ids[0].id,
                    'date': record.payment_date,
                }
                payslip_payment_id = self.env['account.payment'].create(payslip_payment_dict)
                payslip_payment_id.action_post()
                record.request_id.write(
                    {'account_move_id': move.id, 'payment_id': payment_id.id,
                     'payslip_payment_id': payslip_payment_id.id, 'state': 'paid'})
            else:
                record.request_id.write(
                    {'account_move_id': move.id, 'payment_id': payment_id.id, 'state': 'paid'})


class Payment(models.Model):
    _name = 'account.payment'
    _inherit = 'account.payment'

    reward_id = fields.Many2one(comodel_name="hr.end.service.benefit", string="", required=False, )

    def action_post(self):
        res = super(Payment, self).action_post()
        for record in self:
            record.reward_id.state = 'paid'
        return res

    def name_get(self):
        new_format = []
        for rec in self:
            if rec.name:
                result = rec.name
            else:
                result = rec.partner_id.name + ' Payment'
            new_format.append((rec.id, result))
        return new_format
