# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from datetime import datetime


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    advance_salary_id = fields.Many2one('hr.advance.salary', string='Advance Payment')

    @api.model
    def default_get(self, fields):
        """
            Default Get From Advance salary Request.
        """
        rec = super(AccountPayment, self).default_get(fields)
        if self.env.context.get('advance_salary_id'):
            advance_salary = self.env['hr.advance.salary'].browse(self.env.context.get('advance_salary_id'))
            rec.update({
                'payment_type': 'outbound',
                'amount': advance_salary.request_amount,
                'partner_id': advance_salary.employee_id.user_id.partner_id.id,
                'advance_salary_id': advance_salary.id,
                })
        return rec

    def action_post(self):
        """
            Override method for Advance salary request paid time calculate advance salary
        """
        rec = super(AccountPayment, self).action_post()
        if self.env.context.get('advance_salary_id'):
            advance_salary = self.env['hr.advance.salary'].browse(self.env.context.get('advance_salary_id'))
            advance_salary.update({
                'paid_date': datetime.today(),
                'paid_by': self.env.uid,
                'state': 'paid',
                'payment_id': self.id,
                'paid_amount': self.amount})
        return rec

