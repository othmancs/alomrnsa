# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"

    approval_history_ids = fields.One2many('orderline.approval.history', 'order_id', string='Approval History')
    state = fields.Selection(selection_add=[('credit_hold', 'CC Hold'), ('approved', 'Approved')], string='Status',
                             copy=False, default='draft')
    upgrade_approval = fields.Boolean(string='Approval based on Order Limit', copy=False)
    approved_amount = fields.Float(string='Approved Amount', copy=False)

    def action_draft(self):
        res = super(SaleOrder,self).action_draft()
        self.approved_amount = False
        self.upgrade_approval = False
        return res

    def action_confirm(self):
        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        for order in self:
            # if order.order_line and order.state in ['draft', 'credit_hold', 'approved'] and order.partner_id.credit_limit > 0:
            if order.order_line and order.state in ['draft', 'credit_hold'] and order.partner_id.credit_limit > 0:
                # if order.partner_id.credit_limit > 0:
                check_false = self.env['credit.code'].check_approval_status(order)
                if not check_false and order.amount_total > 0.0:
                    order.state = 'credit_hold'
                    return True
            if order.order_line and order.state == 'approved' and order.approved_amount < order.amount_total and order.upgrade_approval:
                raise UserError(_('First reduce order quantity base on your Approved amount!'))
        return super(SaleOrder, self).action_confirm()

    def delivery_order(self):
        for order in self:
            order.action_confirm()
        return True

    def credit_approve(self):
        if not self.env.user.has_group('sales_team.group_sale_manager') and not self.env.user.has_group('account.group_account_manager'):
            raise UserError(_("Only users with '%s' or '%s' rights are allowed to give approval!" % (self.env.ref("sales_team.group_sale_manager").display_name, self.env.ref("account.group_account_manager").display_name)))
        elif self.env.user.id == self.user_id.id:
            raise UserError(_('You can not approve own record!'))
        else:
            view_id = self.env.ref('payment_credit_limit.view_approval_credit_limit', False)
            return {'type': 'ir.actions.act_window',
                    'name': _('Approval Credit Limit'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'approval.credit.limit',
                    'target': 'new',
                    'views': [(view_id.id, 'form')],
                    'view_id': view_id.id,
                    }

    def cancel_order_on_cc(self):
        if not self.env.user.has_group('sales_team.group_sale_manager') and not self.env.user.has_group('account.group_account_manager'):
            raise UserError(_("Only users with '%s' or '%s' rights are allowed to reject approval request!" % (self.env.ref("sales_team.group_sale_manager").display_name, self.env.ref("account.group_account_manager").display_name)))
        elif self.env.user.id == self.user_id.id:
            raise UserError(_('You can not reject own record!'))
        else:
            view_id = self.env.ref('payment_credit_limit.view_cancel_credit_limit', False)
            return {'type': 'ir.actions.act_window',
                    'name': _('Cancel Approval'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'approval.credit.limit',
                    'target': 'new',
                    'views': [(view_id.id, 'form')],
                    'view_id': view_id.id,
                    }
