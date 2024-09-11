# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from datetime import datetime, timedelta

OPERATOR_CONDITION = {
    '==': '=',
    '<=': '>=',
    '<': '>',
    '>=': '<=',
    '>': '<'
}


class CreditCode(models.Model):
    _name = "credit.code"
    _description = "Credit Code"

    def calculate_onorder_amount(self, partner, operator_condition, days, sale_order, partner_currency_id):
        past_due_amt = 0.0
        cr = self.env.cr
        delivery_date = datetime.now().date()
        check_date = delivery_date - timedelta(days=days)
        operator_condition = OPERATOR_CONDITION[operator_condition]
        user_company = self.env.user.company_id.id
        # calculate partner credit amount.
        dates_query = '(l.date_maturity '
        dates_query += operator_condition
        dates_query += ' %s)'
        query = '''SELECT l.id
                FROM account_move_line AS l,
                account_account, account_move am
                WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                    AND (am.state IN ('draft', 'posted'))
                    AND (am.move_type = 'out_invoice')
                    AND (l.partner_id = %s)
                    AND l.company_id = %s
                    AND ''' + dates_query + '''
                    '''
        cr.execute(query, [partner, user_company, check_date])
        aml_ids = cr.fetchall()
        aml_ids = aml_ids and [x[0] for x in aml_ids] or []
        for line in self.env['account.move.line'].browse(aml_ids):
            open_amount = line.balance
            if line.currency_id and line.currency_id.id != partner_currency_id.id:
                open_amount = line.currency_id.compute(open_amount, partner_currency_id)
            past_due_amt += open_amount
        return past_due_amt

    def check_approval_status(self, sale_order):
        partner = self.env['res.partner']._find_accounting_partner(sale_order.partner_id)
        past_due_amt = self.calculate_onorder_amount(partner.id, '>=', 0, sale_order, partner.currency_id)
        past_total_amount = past_due_amt + sale_order.amount_total

        return True if partner.credit_limit >= past_total_amount else False


class OrderlineApprovalHistory(models.Model):
    _name = "orderline.approval.history"
    _description = "Orderline Approval History"

    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user,
                              help="Orderline approval user!")
    date = fields.Date(string='Date', default=lambda self: fields.Date.today(),
                       help="Orderline approval date!")
    approved_amount = fields.Float(string='Approval Amount', help="Orderline approved amount.")
    reason = fields.Text(string='Reason', help="Description about orderline approval history!")
    order_id = fields.Many2one('sale.order', string='Sale Order')
    status = fields.Selection([('draft', '-'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='draft',
                              copy=False, help="Status of orderline approval history!")
