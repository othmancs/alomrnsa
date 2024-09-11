# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import timedelta
from dateutil.relativedelta import relativedelta


class WarrantyDetail(models.Model):
    _name = 'warranty.detail'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Warranty Detail"
    _rec_name = "warranty_no"
    _order = "id desc"

    @api.depends('invoice_id', 'invoice_id.payment_state')
    def check_invoice_paid(self):
        for rec in self:
            rec.is_invoice_paid = True if rec.invoice_id and rec.invoice_id.payment_state == 'paid' else False

    warranty_no = fields.Char(string="Number", copy=False, readonly=True, default=lambda x: _('New'), help="Warranty Number.")
    template_id = fields.Many2one('warranty.template', string="Template", readonly=True, states={'draft': [('readonly', False)]})
    is_renewable = fields.Boolean(string="Is Renewable?", related="template_id.is_renewable", readonly=True, states={'draft': [('readonly', False)]})
    is_renewed = fields.Boolean(string="Renewed", default=False, copy=False, readonly=True, states={'draft': [('readonly', False)]})
    start_date = fields.Date(string="Start Date", copy=False, readonly=True, states={'draft': [('readonly', False)]})
    end_date = fields.Date(string="End Date", copy=False, readonly=True, states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', string="Customer", required=True, readonly=True, states={'draft': [('readonly', False)]})
    partner_phone = fields.Char(string="Phone", readonly=True, states={'draft': [('readonly', False)]})
    partner_email = fields.Char(string="Email", readonly=True, states={'draft': [('readonly', False)]})
    user_id = fields.Many2one('res.users', string="Salesperson", required=True, readonly=True, states={'draft': [('readonly', False)]})
    tag_ids = fields.Many2many('crm.tag', string="Tags", readonly=True, states={'draft': [('readonly', False)]})
    product_id = fields.Many2one('product.product', string="Product", required=True, readonly=True, states={'draft': [('readonly', False)]})
    serial_id = fields.Many2one('stock.lot', string="Serial No.", readonly=True, states={'draft': [('readonly', False)]})
    sale_id = fields.Many2one('sale.order', string="Order", readonly=True, states={'draft': [('readonly', False)]})
    sale_line_id = fields.Many2one('sale.order.line', string="Order Line", readonly=True, states={'draft': [('readonly', False)]})
    sale_invoice_id = fields.Many2one('account.move', string="Sale Invoice", copy=False, readonly=True, states={'draft': [('readonly', False)]})
    invoice_id = fields.Many2one('account.move', string="Invoice", copy=False, readonly=True, states={'draft': [('readonly', False)]})
    is_invoice_paid = fields.Boolean(string="Is paid?", compute='check_invoice_paid', store=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company, readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'),
                                ('pending', 'Pending'),
                                ('confirm', 'Confirmed'),
                                ('running', 'Running'),
                                ('expired', 'Expired'),
                                ('cancel', 'Cancelled')], string="Status", default='draft', copy=False)
    confirm_by = fields.Many2one('res.users', string="Confirmed By", copy=False, readonly=True)
    confirm_date = fields.Datetime(string="Confirmed Date", copy=False, readonly=True)
    cancel_by = fields.Many2one('res.users', string="Cancelled By", copy=False, readonly=True)
    cancel_date = fields.Datetime(string="Cancelled Date", copy=False, readonly=True)
    expired_by = fields.Many2one('res.users', string="Expired By", copy=False, readonly=True)
    expired_date = fields.Datetime(string="Expired Date", copy=False, readonly=True)
    parent_id = fields.Many2one('warranty.detail', string="Parent", readonly=True, states={'draft': [('readonly', False)]})
    warranty_info = fields.Text(string="Warranty Info", readonly=True, states={'draft': [('readonly', False)]})
    warranty_cost = fields.Float(string="Warranty Cost", default=0.0, readonly=True)
    warranty_tc = fields.Text(string="Terms & Conditions", readonly=True, states={'draft': [('readonly', False)]})
    warranty_renew_cost = fields.Float(string="Renew Cost", default=0.0, readonly=True)
    warranty_ids = fields.One2many('warranty.detail', 'parent_id', string="Warranty History", readonly=True, states={'draft': [('readonly', False)]})


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals['template_id']:
                war_temp = self.env['warranty.template'].browse(vals['template_id'])
                vals['warranty_cost'] = war_temp.warranty_cost
            if not vals.get('warranty_no'):
                vals['warranty_no'] = self.env['ir.sequence'].next_by_code('warranty.detail') or _('New')
        return super(WarrantyDetail, self).create(vals_list)

    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'cancel'):
                raise UserError(_('You can not delete a warranty which are not in draft or cancel state! Try to cancel it before.'))
        return super(WarrantyDetail, self).unlink()

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.sale_id = False
        if self.partner_id:
            self.partner_phone = self.partner_id.phone
            self.partner_email = self.partner_id.email

    @api.onchange('sale_id')
    def onchage_sale_order(self):
        self.sale_line_id = False

    @api.onchange('product_id')
    def onchage_product(self):
        self.serial_id = False

    @api.onchange('sale_line_id')
    def onchange_sale_line(self):
        self.product_id = False
        if self.sale_line_id:
            self.product_id = self.sale_line_id.product_id.id

    @api.onchange('template_id')
    def onchange_template_id(self):
        if self.template_id:
            current_date = fields.Date.today()
            months = self.template_id.warranty_months if not self.parent_id else self.template_id.warranty_renew_months
            self.start_date = current_date
            self.end_date = current_date + relativedelta(months=months)
            self.warranty_cost = self.template_id.warranty_cost
            self.warranty_renew_cost = self.template_id.warranty_renew_cost
            self.warranty_info = self.template_id.warranty_info
            self.warranty_tc = self.template_id.warranty_tc

    def action_view_invoice(self):
        """
            Show invoices
        """
        if self.invoice_id:
            action = self.env.ref('account.action_move_out_invoice_type').read()[0]
            if len(self.invoice_id) > 1:
                action['domain'] = [('id', '=', self.invoice_id.id)]
            elif len(self.invoice_id) == 1:
                action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
                action['res_id'] = self.invoice_id.id
            else:
                action = {'type': 'ir.actions.act_window_close'}
            return action

    def action_view_parent_warranty(self):
        """
            Show parent warranty
        """
        if self.parent_id:
            action = self.env.ref('sales_warranty.warranty_detail_action_all').read()[0]
            if len(self.parent_id) > 1:
                action['domain'] = [('id', '=', self.partner_id.id)]
            elif len(self.parent_id) == 1:
                action['views'] = [(self.env.ref('sales_warranty.warranty_detail_form_view').id, 'form')]
                action['res_id'] = self.parent_id.id
            else:
                action = {'type': 'ir.actions.act_window_close'}
            return action

    def action_view_child_warranties(self):
        """
            Show child warranty
        """
        if self.warranty_ids:
            action = self.env.ref('sales_warranty.warranty_detail_action_all').read()[0]
            if len(self.warranty_ids) > 1:
                action['domain'] = [('id', 'in', self.warranty_ids.ids)]
            elif len(self.warranty_ids) == 1:
                action['views'] = [(self.env.ref('sales_warranty.warranty_detail_form_view').id, 'form')]
                action['res_id'] = self.warranty_ids[0].id
            else:
                action = {'type': 'ir.actions.act_window_close'}
            return action

    def action_create_invoice(self):
        """
            Create invoice for the warranty
        """
        inv_obj = self.env['account.move']
        journal_id = self.env['account.journal'].search([('type', '=', 'sale')],limit=1)
        if not journal_id:
            raise UserError(_('Please define an accounting sales journal for this company.'))
        invoice_vals = {
            'name': self.warranty_no,
            'invoice_origin': self.warranty_no,
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'partner_shipping_id': self.partner_id.id,
            'journal_id': journal_id.id,
            'currency_id': self.company_id.currency_id.id,
            'narration': self.warranty_info,
            'company_id': self.company_id.id,
            'user_id': self.user_id and self.user_id.id,
        }
        invoice = inv_obj.create(invoice_vals)
        account = self.product_id.property_account_income_id or self.product_id.categ_id.property_account_income_categ_id
        if not account:
            raise UserError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                (self.product_id.name, self.product_id.id, self.product_id.categ_id.name))

        if self.parent_id:
            if self.warranty_renew_cost <= 0.0:
                raise UserError('Warranty Renew cost should be grater than 0.0')
            price_unit = self.warranty_renew_cost
        else:
            if self.warranty_cost <= 0.0:
                raise UserError('Warranty cost should be grater than 0.0')
            price_unit = self.warranty_cost
        invoice.invoice_line_ids = [(0, 0, {
                'name': self.warranty_no,
                'ref': self.warranty_no,
                'account_id': account.id,
                'price_unit': price_unit,
                'quantity': 1.0,
                'product_uom_id': self.product_id.uom_id.id,
                'product_id': self.product_id.id or False,
                'tax_ids': [(6, 0, self.product_id.taxes_id.ids)],
            })]
        self.invoice_id = invoice.id
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
        action['res_id'] = invoice.id
        return action

    def action_confirm(self):
        self.confirm_by = self.env.uid
        self.confirm_date = fields.Datetime.now()
        self.state = 'confirm'

    def action_pending(self):
        self.state = 'pending'

    def action_running(self):
        current_date = fields.Date.today()
        months = self.template_id.warranty_months if not self.parent_id else self.template_id.warranty_renew_months
        self.start_date = current_date
        if self.template_id:
            self.end_date = current_date + relativedelta(months=months)
        self.state = 'running'
        running_template_id = self.env.ref('sales_warranty.warranty_running_email')
        if running_template_id:
            running_template_id.send_mail(self.id, force_send=True, raise_exception=False)

    def action_cancel(self):
        self.cancel_by = self.env.uid
        self.cancel_date = fields.Datetime.now()
        self.state = 'cancel'

    def set_to_draft(self):
        self.state = 'draft'

    def action_expiry(self):
        self.state = 'expired'
        self.expired_by = self.env.uid
        self.expired_date = fields.Datetime.now()
        try:
            template_id = self.env.ref('sales_warranty.warranty_expire_email')
        except ValueError:
            template_id = False
        if template_id:
            template_id.send_mail(self.id, force_send=True, raise_exception=False)

    def action_renew(self):
        warranty_start_date = fields.Date.today() if self.state == 'expired' else self.end_date
        renew_id = self.copy(default={
                'start_date': warranty_start_date,
                'end_date': warranty_start_date + relativedelta(months=self.template_id.warranty_renew_months),
                'parent_id': self.id,
                'warranty_info': self.template_id.warranty_info,
                'warranty_tc': self.template_id.warranty_tc,
                'warranty_renew_cost': self.template_id.warranty_renew_cost,
            })
        self.is_renewed = True
        action = self.env.ref('sales_warranty.warranty_detail_action_all').read()[0]
        action['views'] = [(self.env.ref('sales_warranty.warranty_detail_form_view').id, 'form')]
        action['res_id'] = renew_id.id
        return action

    @api.model
    def scheduler_check_warranty(self):
        """
            Scheduler for check warranty expiry
        """
        current_date = fields.Date.today()
        for rec in self.search([('state', '=', 'running')]):
            if rec.end_date:
                if current_date == rec.end_date:
                    rec.action_expiry()
                before_expiry_date = rec.end_date - timedelta(days=10)
                expirey_template_id = self.env.ref('sales_warranty.warranty_expiration_email')
                if before_expiry_date == current_date and expirey_template_id and rec.is_renewable:
                    expirey_template_id.send_mail(rec.id, force_send=True, raise_exception=False)
