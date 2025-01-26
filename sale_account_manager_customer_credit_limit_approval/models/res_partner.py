# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    credit_check = fields.Boolean('Active Credit', help='Activate the credit limit feature')
    credit_warning = fields.Monetary('Warning Amount')
    credit_blocking = fields.Monetary('Blocking Amount')
    amount_due = fields.Monetary('Due Amount', compute='_compute_amount_due')

    @api.depends('credit', 'debit')
    def _compute_amount_due(self):
        for rec in self:
            rec.amount_due = rec.credit - rec.debit
            partner_so = self.env['sale.order'].search([('partner_id', '=', rec.id), ('state', '=', 'sale')])
            for order in partner_so:
                if not order.invoice_ids:
                    rec.amount_due = rec.amount_due + order.amount_total
                else:
                    draft_invoice = order.invoice_ids.filtered(lambda x: x.state == 'draft')
                    rec.amount_due = rec.amount_due + sum(draft_invoice.mapped('amount_residual'))
                
    @api.constrains('credit_warning', 'credit_blocking')
    def _check_credit_amount(self):
        for credit in self:
            if credit.credit_warning > credit.credit_blocking:
                raise ValidationError(_('Warning amount should not be greater than blocking amount.'))
            if credit.credit_warning < 0 or credit.credit_blocking < 0:
                raise ValidationError(_('Warning amount or blocking amount should not be less than zero.'))


class ResCompany(models.Model):
    _inherit = 'res.company'

    accountant_email = fields.Char(string='Accountant email')