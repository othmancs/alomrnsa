# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_po_refund = fields.Boolean(string="Is PO Refund", )
    # is_all_receipts = fields.Boolean(string="Is All Receipts", )
    is_all_receipts = fields.Boolean(string="Is All Receipts", compute="compute_all_receipts", store=True)
    po_id = fields.Many2one(comodel_name="purchase.order", string="Source PO", required=False, )

    @api.depends('order_line.qty_received')
    def compute_all_receipts(self):
        for rec in self:
            picking = self.env['stock.picking'].search([('origin', '=', rec.name)])
            if picking:
                rec.is_all_receipts = True
                for pick in picking:
                    if pick.state != "done":
                        rec.is_all_receipts = False
                        break
            else:
                rec.is_all_receipts = False

    @api.model_create_multi
    def create(self, vals_list):
        orders = self.browse()
        partner_vals_list = []
        for vals in vals_list:
            # raise UserError(_("'vals': %s" % vals))
            company_id = vals.get('company_id', self.default_get(['company_id'])['company_id'])
            # Ensures default picking type and currency are taken from the right company.
            self_comp = self.with_company(company_id)
            if vals.get('name', 'New') == 'New':
                seq_date = None
                if 'date_order' in vals:
                    seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))

                if vals.get('is_po_refund'):
                    vals['name'] = self_comp.env['ir.sequence'].next_by_code('refund_purchase_order',
                                                                             sequence_date=seq_date) or '/'
                else:
                    vals['name'] = self_comp.env['ir.sequence'].next_by_code('purchase.order',
                                                                             sequence_date=seq_date) or '/'
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
            if vals.get('is_po_refund'):
                vals['name'] = self_comp.env['ir.sequence'].next_by_code('refund_purchase_order',
                                                                         sequence_date=seq_date) or '/'
            # else:
            #     vals['name'] = self_comp.env['ir.sequence'].next_by_code('purchase.order',
            #                                                              sequence_date=seq_date) or '/'
            vals, partner_vals = self._write_partner_values(vals)
            partner_vals_list.append(partner_vals)
            orders |= super(PurchaseOrder, self_comp).create(vals)
        for order, partner_vals in zip(orders, partner_vals_list):
            if partner_vals:
                order.sudo().write(partner_vals)  # Because the purchase user doesn't have write on `res.partner`
        return orders

    def create_po_refund(self):
        # raise UserError(_('%s' % self.copy_data()[0]))
        # get_pos = self.env['purchase.order'].search([('name', '=', 'R%s' % self.name), ('state', '!=', 'cancel')])
        # if get_pos:
        #     raise UserError(_('This PO has a refund created before R%s' % self.name))

        new_order_vals = self.copy_data()[0]
        for line in new_order_vals['order_line']:
            line[2]['product_qty'] = line[2]['product_qty'] * -1
        new_order_vals['is_po_refund'] = True
        new_order_vals['po_id'] = self.id
        # new_order_vals['name'] = 'R' + self.name
        new_order = self.create(new_order_vals)
        return True

    def button_confirm(self):
        if self.is_po_refund:
            for line in self.order_line:
                if line.product_qty >= 0.00:
                    raise UserError(_("You cannot confirm the PO Refund with positive QTY."))
        res = super().button_confirm()
        return res

    def po_refund_smart_button(self):
        return {
            'name': 'PO Refunds',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
            'domain': [('po_id', '=', self.id)]
        }

