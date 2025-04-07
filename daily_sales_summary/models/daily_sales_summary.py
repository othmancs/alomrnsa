# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import timedelta
from collections import defaultdict
import logging

_logger = logging.getLogger(__name__)

class DailySalesSummary(models.Model):
    _name = 'daily.sales.summary'
    _description = 'ملخص حركة المبيعات اليومية'
    _rec_name = 'date_from'
    _order = 'date_from desc'

    date_from = fields.Date(string='من تاريخ', default=fields.Date.today, required=True)
    date_to = fields.Date(string='إلى تاريخ', default=fields.Date.today, required=True)
    company_id = fields.Many2one(
        'res.company', 
        string='الشركة',
        default=lambda self: self.env.company,
        required=True
    )
    branch_id = fields.Many2one(
        'res.branch',
        string='الفرع'
    )
    company_currency_id = fields.Many2one(
        'res.currency',
        string='العملة',
        related='company_id.currency_id',
        store=True
    )

    # الحقول المحسوبة
    cash_sales = fields.Monetary(
        string='مبيعات نقدية مدفوعة بتاريخه قبل الضريبة',
        currency_field='company_currency_id',
        compute='_compute_sales_totals'
    )
    total_tax = fields.Monetary(
        string='مجموع الضريبة فقط',
        currency_field='company_currency_id',
        compute='_compute_sales_totals'
    )
    partial_sales = fields.Monetary(
        string='مبيعات مدفوع جزئي',
        currency_field='company_currency_id,
        compute='_compute_sales_totals'
    )
    credit_sales = fields.Monetary(
        string='مبيعات آجلة غير مدفوعة',
        currency_field='company_currency_id',
        compute='_compute_sales_totals'
    )
    cash_refunds = fields.Monetary(
        string='إرجاعات مسترد المبلغ',
        currency_field='company_currency_id',
        compute='_compute_refund_totals'
    )
    credit_refunds = fields.Monetary(
        string='إرجاعات غير مسترد المبلغ',
        currency_field='company_currency_id',
        compute='_compute_refund_totals'
    )
    cash_box = fields.Monetary(
        string='المقبوضات',
        currency_field='company_currency_id',
        compute='_compute_cash_box'
    )
    total_cash = fields.Monetary(
        string='إجمالي الصندوق',
        currency_field='company_currency_id',
        compute='_compute_total_cash'
    )
    payment_method_totals = fields.Html(
        string='المجاميع حسب طريقة الدفع',
        compute='_compute_payment_method_totals',
        sanitize=False
    )

    @api.depends('date_from', 'date_to', 'company_id', 'branch_id')
    def _compute_payment_method_totals(self):
        for record in self:
            try:
                payment_data = self._get_payment_method_data(record)
                record.payment_method_totals = self._generate_payment_html(payment_data, record)
            except Exception as e:
                _logger.error("Error in payment_method_totals: %s", str(e))
                record.payment_method_totals = f"""
                <div class="alert alert-danger">
                    خطأ في حساب طرق الدفع: {str(e)}
                </div>
                """

    def _get_payment_method_data(self, record):
        payment_method_data = defaultdict(float)
        
        # الفواتير المدفوعة بالكامل
        cash_invoices = self.env['account.move'].search([
            ('invoice_date', '>=', record.date_from),
            ('invoice_date', '<=', record.date_to),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', '=', 'paid'),
            ('company_id', '=', record.company_id.id),
        ])
        
        # الفواتير المدفوعة جزئياً
        partial_invoices = self.env['account.move'].search([
            ('invoice_date', '>=', record.date_from),
            ('invoice_date', '<=', record.date_to),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', '=', 'partial'),
            ('company_id', '=', record.company_id.id),
        ])
        
        # المدفوعات المباشرة
        payments = self.env['account.payment'].search([
            ('date', '>=', record.date_from),
            ('date', '<=', record.date_to),
            ('payment_type', '=', 'inbound'),
            ('state', '=', 'posted'),
            ('is_internal_transfer', '=', False),
            ('company_id', '=', record.company_id.id),
        ])

        # تجميع البيانات
        for invoice in cash_invoices + partial_invoices:
            for payment in invoice._get_reconciled_payments():
                if payment.payment_method_line_id:
                    method = payment.payment_method_line_id
                    payment_method_data[method] += payment.amount

        for payment in payments:
            if payment.payment_method_line_id:
                method = payment.payment_method_line_id
                payment_method_data[method] += payment.amount

        return payment_method_data

    def _generate_payment_html(self, payment_data, record):
        if not payment_data:
            return "<div class='alert alert-info'>لا توجد مدفوعات في الفترة المحددة</div>"
        
        rows = []
        for method, amount in sorted(payment_data.items(), key=lambda x: x[1], reverse=True):
            rows.append(f"""
            <tr>
                <td>{method.name}</td>
                <td class='text-right'>{amount:,.2f} {record.company_currency_id.symbol}</td>
            </tr>
            """)
        
        return f"""
        <div class="table-responsive">
            <table class="table table-bordered table-hover">
                <thead class="thead-light">
                    <tr>
                        <th>طريقة الدفع</th>
                        <th class='text-right'>المبلغ</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                </tbody>
            </table>
        </div>
        """

    @api.depends('date_from', 'date_to', 'company_id', 'branch_id')
    def _compute_sales_totals(self):
        for record in self:
            # حساب المبيعات النقدية (مدفوع بالكامل في نفس التاريخ)
            cash_domain = [
                ('invoice_date', '>=', record.date_from),
                ('invoice_date', '<=', record.date_to),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', '=', 'paid'),
                ('company_id', '=', record.company_id.id)
            ]
            if record.branch_id:
                cash_domain.append(('branch_id', '=', record.branch_id.id))
            cash_invoices = self.env['account.move'].search(cash_domain)
            record.cash_sales = sum(invoice.amount_untaxed for invoice in cash_invoices)
            record.total_tax = sum(invoice.amount_tax for invoice in cash_invoices)

            # حساب المبيعات المدفوعة جزئياً (نعرض المبلغ المدفوع فقط)
            partial_domain = [
                ('invoice_date', '>=', record.date_from),
                ('invoice_date', '<=', record.date_to),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', '=', 'partial'),
                ('company_id', '=', record.company_id.id)
            ]
            if record.branch_id:
                partial_domain.append(('branch_id', '=', record.branch_id.id))
            partial_invoices = self.env['account.move'].search(partial_domain)
            record.partial_sales = sum(invoice.amount_total - invoice.amount_residual for invoice in partial_invoices)

            # حساب المبيعات الآجلة (غير مدفوع)
            credit_domain = [
                ('invoice_date', '>=', record.date_from),
                ('invoice_date', '<=', record.date_to),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', '=', 'not_paid'),
                ('company_id', '=', record.company_id.id)
            ]
            if record.branch_id:
                credit_domain.append(('branch_id', '=', record.branch_id.id))
            credit_invoices = self.env['account.move'].search(credit_domain)
            record.credit_sales = sum(invoice.amount_untaxed for invoice in credit_invoices)

    @api.depends('date_from', 'date_to', 'company_id', 'branch_id')
    def _compute_refund_totals(self):
        for record in self:
            # حساب المرتجعات النقدية (مدفوع)
            cash_refund_domain = [
                ('invoice_date', '>=', record.date_from),
                ('invoice_date', '<=', record.date_to),
                ('move_type', '=', 'out_refund'),
                ('state', '=', 'posted'),
                ('payment_state', '=', 'paid'),
                ('company_id', '=', record.company_id.id)
            ]
            if record.branch_id:
                cash_refund_domain.append(('branch_id', '=', record.branch_id.id))
            cash_refunds = self.env['account.move'].search(cash_refund_domain)
            record.cash_refunds = sum(refund.amount_untaxed for refund in cash_refunds)

            # حساب مرتجعات الآجل (غير مدفوع)
            credit_refund_domain = [
                ('invoice_date', '>=', record.date_from),
                ('invoice_date', '<=', record.date_to),
                ('move_type', '=', 'out_refund'),
                ('state', '=', 'posted'),
                ('payment_state', '=', 'not_paid'),
                ('company_id', '=', record.company_id.id)
            ]
            if record.branch_id:
                credit_refund_domain.append(('branch_id', '=', record.branch_id.id))
            credit_refunds = self.env['account.move'].search(credit_refund_domain)
            record.credit_refunds = sum(refund.amount_untaxed for refund in credit_refunds)

    @api.depends('date_from', 'date_to', 'company_id', 'branch_id')
    def _compute_cash_box(self):
        for record in self:
            # حساب المقبوضات (الدفعات)
            payment_domain = [
                ('date', '>=', record.date_from),
                ('date', '<=', record.date_to),
                ('payment_type', '=', 'inbound'),
                ('state', '=', 'posted'),
                ('is_internal_transfer', '=', False),
                ('company_id', '=', record.company_id.id)
            ]
            if record.branch_id:
                payment_domain.append(('branch_id', '=', record.branch_id.id))
            payments = self.env['account.payment'].search(payment_domain)
            record.cash_box = sum(payment.amount for payment in payments)

    @api.depends('cash_box', 'cash_refunds')
    def _compute_total_cash(self):
        for record in self:
            record.total_cash = record.cash_box - record.cash_refunds

    @api.onchange('date_from')
    def _onchange_date_from(self):
        if self.date_from and not self.date_to:
            self.date_to = self.date_from

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_from and record.date_to and record.date_from > record.date_to:
                raise models.ValidationError("تاريخ البداية يجب أن يكون قبل تاريخ النهاية")

    def action_view_cash_sales(self):
        self.ensure_one()
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        domain = [
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', '=', 'paid'),
            ('company_id', '=', self.company_id.id)
        ]
        if self.branch_id:
            domain.append(('branch_id', '=', self.branch_id.id))
        action['domain'] = domain
        action['context'] = {
            'search_default_invoice': 1,
            'create': False
        }
        return action

    def action_view_partial_sales(self):
        self.ensure_one()
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        domain = [
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', '=', 'partial'),
            ('company_id', '=', self.company_id.id)
        ]
        if self.branch_id:
            domain.append(('branch_id', '=', self.branch_id.id))
        action['domain'] = domain
        action['context'] = {
            'search_default_invoice': 1,
            'create': False
        }
        return action

    def action_view_credit_sales(self):
        self.ensure_one()
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        domain = [
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', '=', 'not_paid'),
            ('company_id', '=', self.company_id.id)
        ]
        if self.branch_id:
            domain.append(('branch_id', '=', self.branch_id.id))
        action['domain'] = domain
        action['context'] = {
            'search_default_invoice': 1,
            'create': False
        }
        return action

    def action_view_cash_refunds(self):
        self.ensure_one()
        action = self.env.ref('account.action_move_out_refund_type').read()[0]
        domain = [
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('move_type', '=', 'out_refund'),
            ('state', '=', 'posted'),
            ('payment_state', '=', 'paid'),
            ('company_id', '=', self.company_id.id)
        ]
        if self.branch_id:
            domain.append(('branch_id', '=', self.branch_id.id))
        action['domain'] = domain
        action['context'] = {
            'search_default_refund': 1,
            'create': False
        }
        return action

    def action_view_credit_refunds(self):
        self.ensure_one()
        action = self.env.ref('account.action_move_out_refund_type').read()[0]
        domain = [
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('move_type', '=', 'out_refund'),
            ('state', '=', 'posted'),
            ('payment_state', '=', 'not_paid'),
            ('company_id', '=', self.company_id.id)
        ]
        if self.branch_id:
            domain.append(('branch_id', '=', self.branch_id.id))
        action['domain'] = domain
        action['context'] = {
            'search_default_refund': 1,
            'create': False
        }
        return action

    def action_view_cash_box(self):
        self.ensure_one()
        action = self.env.ref('account.action_account_payments').read()[0]
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('payment_type', '=', 'inbound'),
            ('state', '=', 'posted'),
            ('is_internal_transfer', '=', False),
            ('company_id', '=', self.company_id.id)
        ]
        if self.branch_id:
            domain.append(('branch_id', '=', self.branch_id.id))
        action['domain'] = domain
        action['context'] = {
            'default_payment_type': 'inbound',
            'create': False
        }
        return action
