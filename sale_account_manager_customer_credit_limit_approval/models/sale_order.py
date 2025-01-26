# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import api, models, fields, _
from odoo.exceptions import AccessDenied


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection=[
            ('draft', "Quotation"),
            ('sent', "Quotation Sent"),
            ('sales_approval', "Sales Approval"),
            ('finance_approval', "Finance Approval"),
            ('approved', "Approved"),
            ('reject', "Rejected"),
            ('sale', "Sales Order"),
            ('done', "Locked"),
            ('cancel', "Cancelled"),
        ],
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft')
    amount_due = fields.Monetary(related='partner_id.amount_due', currency_field='company_currency_id')
    customer_blocking_limit = fields.Monetary(related='partner_id.credit_blocking', currency_field='company_currency_id')
    company_currency_id = fields.Many2one(string='Company Currency', readonly=True,
                                          related='company_id.currency_id')

    def get_so_for_approval(self):
        web = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        so_base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url') + '/web#id=%d&menu_id=%d&cids=%d&action=%d&model=sale.order&view_type=form' % (
                          self.id, self.env.ref('sale.sale_menu_root').id,
                          self.env.company.id,
                          self.env.ref('sale.action_quotations_with_onboarding').id)
        return so_base_url

    @api.depends('amount_due')
    def _compute_customer_credit_limit(self):
        self.is_credit_limit_approval = False
        if self.partner_id or self.amount_due:
            if (self.amount_due + self.amount_total) > self.customer_blocking_limit and \
            not self.is_credit_limit_final_approved:
                self.is_credit_limit_approval = True
            if self.partner_id.credit_blocking <= self.amount_due and self.state in ['draft', 'sent']:
                self.is_credit_limit_approval = True
            elif self.amount_total and (self.amount_due + self.amount_total) > self.customer_blocking_limit:
                self.is_credit_limit_approval = True
        else:
            self.is_credit_limit_approval = False

    is_credit_limit_approval = fields.Boolean(compute='_compute_customer_credit_limit')
    is_credit_limit_final_approved = fields.Boolean()

    def action_confirm(self):
        '''
        Check the partner credit limit and exisiting due of the partner
        before confirming the order. The order is only blocked if exisitng
        due is greater than blocking limit of the partner.
        '''
        partner_id = self.partner_id
        total_amount = self.amount_due
        if partner_id.credit_check:
            existing_move = self.env['account.move'].search(
                [('partner_id', '=', self.partner_id.id), ('state', '=', 'posted')])
            if (self.amount_due + self.amount_total) > self.customer_blocking_limit and\
             not self.is_credit_limit_final_approved:
                difference_amount = round((self.amount_due + self.amount_total) - self.customer_blocking_limit, 2)
                raise AccessDenied(_('Can not confirm the respective S.O as \
                    Customer has crossed their Approved credit limit by %s Please seek for approval to proceed'\
                     % difference_amount))
            elif partner_id.credit_blocking <= total_amount and not existing_move:
                view_id = self.env.ref('sale_account_manager_customer_credit_limit_approval.view_warning_wizard_form')
                context = dict(self.env.context or {})
                context[
                    'message'] = "Customer Blocking limit exceeded without having a recievable, Do You want to continue?"
                context['default_sale_id'] = self.id
                if not self._context.get('warning'):
                    return {
                        'name': 'Warning',
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'warning.wizard',
                        'view_id': view_id.id,
                        'target': 'new',
                        'context': context,
                    }
            elif partner_id.credit_warning <= total_amount and partner_id.credit_blocking > total_amount:
                view_id = self.env.ref('sale_account_manager_customer_credit_limit_approval.view_warning_wizard_form')
                context = dict(self.env.context or {})
                context['message'] = "Customer warning limit exceeded, Do You want to continue?"
                context['default_sale_id'] = self.id
                if not self._context.get('warning'):
                    return {
                        'name': 'Warning',
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'warning.wizard',
                        'view_id': view_id.id,
                        'target': 'new',
                        'context': context,
                    }
            elif partner_id.credit_blocking <= total_amount and not self.is_credit_limit_final_approved:
                raise AccessDenied(_('Customer credit limit exceeded.'))
        res = super(SaleOrder, self).action_confirm()
        return res

    def send_credit_limit_approval(self):
        template_id = self.env.ref('sale_account_manager_customer_credit_limit_approval.sale_order_credit_limit_approval_sales_manager')
        template_id.with_context().send_mail(self._origin.id, force_send=True)
        msg = "Send For Credit Limit Approval To: %s" % self.partner_id.user_id.name or ""
        self.message_post(body=msg)
        self.state = 'sales_approval'
        self.is_credit_limit_approval = False

    def approved_credit_limit_from_sales_manager(self):
        if self.state == 'sales_approval':
            template_id = self.env.ref('sale_account_manager_customer_credit_limit_approval.sale_order_credit_limit_approval_account_manager')
            template_id.with_context().send_mail(self._origin.id, force_send=True)
            msg = "Send For Credit Limit Approval To Finance Team"
            self.message_post(body=msg)
            self.state = 'finance_approval'

    def approved_credit_limit_from_account_manager(self):
        if self.state == 'finance_approval':
            self.state = 'approved'
            self.is_credit_limit_final_approved = True


    def reject_sale_order(self):
        if self.state == 'sales_approval':
            template_data = {
                'subject': 'Customer credit limit rejected',
                'body_html': """<p>
                Hello %s, <br/><br/>
                </p>
                <p>
                This email is to notify that Quotation number %s which belongs to %s 
                has been rejected by %s (Customer Account Manager), <br/> please reach him for further clarifications </p>
                """ % (self.user_id.name, self.name, self.partner_id.name, self.env.user.name),
                'email_from': self.env.user.partner_id.email or self.env.user.email,
                'email_to': self.user_id.email or self.user_id.partner_id.email,
                'record_name': self.name,
            }
            template_id = self.env['mail.mail'].create(template_data)
            template_id.sudo().send()
            self.state = 'reject'
            msg = "Rejected By Sales Manager: %s" % self.env.user.name
            self.message_post(body=msg)
        elif self.state == 'finance_approval':
            template_data = {
                'subject': 'Customer credit limit rejected',
                'body_html': """<p>
                Hello %s, <br/><br/>
                </p>
                <p>
                This email is to notify that Quotation number %s which belongs to %s 
                has been rejected by Finance team, <br/>

                please reach him for further clarifications</p> 
                """ % (self.user_id.name, self.name, self.partner_id.name),
                'email_from': self.env.user.partner_id.email or self.env.user.email,
                'email_to': self.user_id.email or self.user_id.partner_id.email,
                'record_name': self.name,
            }
            template_id = self.env['mail.mail'].create(template_data)
            template_id.sudo().send()
            self.state = 'reject'
            msg = "Rejected By Finance Team: %s" % self.env.user.name
            self.message_post(body=msg)
