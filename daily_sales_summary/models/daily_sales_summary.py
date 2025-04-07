from odoo import models, fields, api
from datetime import timedelta

class DailySalesSummary(models.Model):
    _name = 'daily.sales.summary'
    _description = 'ملخص حركة المبيعات اليومية'
    _rec_name = 'date_from'
    _order = 'date_from desc'

    date_from = fields.Date(string='من تاريخ', default=fields.Date.today(), required=True)
    date_to = fields.Date(string='إلى تاريخ', default=fields.Date.today(), required=True)
    company_id = fields.Many2one(
        'res.company', string='الشركة',
        default=lambda self: self.env.company, required=True
    )
    branch_id = fields.Many2one(
        'res.branch',
        string='الفرع',
        help='تصفية النتائج حسب الفرع المحدد'
    )
    company_currency_id = fields.Many2one(
        'res.currency', string='العملة',
        related='company_id.currency_id', store=True
    )

    # الحقول المحسوبة
    cash_sales = fields.Monetary(
        string='مبيعات نقدية مدفوعة بتاريخه',
        currency_field='company_currency_id',
        compute='_compute_sales_totals', store=True
    )
    partial_payments = fields.Monetary(
        string='مبيعات مدفوع جزئي (المبلغ المدفوع)',
        currency_field='company_currency_id',
        compute='_compute_partial_payments', store=True
    )
    credit_sales = fields.Monetary(
        string='مبيعات آجلة غير مدفوعة',
        currency_field='company_currency_id',
        compute='_compute_sales_totals', store=True
    )
    cash_refunds = fields.Monetary(
        string='إرجاعات مسترد المبلغ',
        currency_field='company_currency_id',
        compute='_compute_refund_totals', store=True
    )
    credit_refunds = fields.Monetary(
        string='إرجاعات غير مسترد المبلغ',
        currency_field='company_currency_id',
        compute='_compute_refund_totals', store=True
    )
    cash_box = fields.Monetary(
        string='المقبوضات',
        currency_field='company_currency_id',
        compute='_compute_cash_box', store=True
    )
    total_cash = fields.Monetary(
        string='إجمالي الصندوق',
        currency_field='company_currency_id',
        compute='_compute_total_cash', store=True
    )
    payment_method_lines = fields.One2many(
        'daily.sales.payment.method',
        'summary_id',
        string='حركات السداد حسب طريقة الدفع',
        compute='_compute_payment_method_lines'
    )

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
    def _compute_partial_payments(self):
        for record in self:
            # حساب المبالغ المدفوعة للفواتير المدفوعة جزئياً
            partial_domain = [
                ('date', '>=', record.date_from),
                ('date', '<=', record.date_to),
                ('payment_type', '=', 'inbound'),
                ('state', '=', 'posted'),
                ('is_internal_transfer', '=', False),
                ('company_id', '=', record.company_id.id),
                ('reconciled_invoice_ids.payment_state', '=', 'partial')
            ]
            if record.branch_id:
                partial_domain.append(('branch_id', '=', record.branch_id.id))
            
            partial_payments = self.env['account.payment'].search(partial_domain)
            record.partial_payments = sum(payment.amount for payment in partial_payments)

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
            # حساب إجمالي الصندوق
            record.total_cash = record.cash_box - record.cash_refunds

    @api.depends('date_from', 'date_to', 'company_id', 'branch_id')
    def _compute_payment_method_lines(self):
        for record in self:
            payment_method_lines = self.env['daily.sales.payment.method']
            
            # Get all payments in the date range
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
            
            # Group by payment method and journal
            payment_groups = {}
            for payment in payments:
                key = (payment.payment_method_line_id.id, payment.journal_id.id)
                if key not in payment_groups:
                    payment_groups[key] = {
                        'payment_method_line_id': payment.payment_method_line_id.id,
                        'journal_id': payment.journal_id.id,
                        'amount': 0.0
                    }
                payment_groups[key]['amount'] += payment.amount
            
            # Create payment method lines
            for key, vals in payment_groups.items():
                payment_method_lines |= payment_method_lines.create({
                    'summary_id': record.id,
                    'payment_method_line_id': vals['payment_method_line_id'],
                    'journal_id': vals['journal_id'],
                    'amount': vals['amount']
                })
            
            record.payment_method_lines = payment_method_lines

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

    def action_view_partial_payments(self):
        self.ensure_one()
        action = self.env.ref('account.action_account_payments').read()[0]
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('payment_type', '=', 'inbound'),
            ('state', '=', 'posted'),
            ('is_internal_transfer', '=', False),
            ('company_id', '=', self.company_id.id),
            ('reconciled_invoice_ids.payment_state', '=', 'partial')
        ]
        if self.branch_id:
            domain.append(('branch_id', '=', self.branch_id.id))
        action['domain'] = domain
        action['context'] = {
            'default_payment_type': 'inbound',
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


class DailySalesPaymentMethod(models.Model):
    _name = 'daily.sales.payment.method'
    _description = 'حركات السداد حسب طريقة الدفع'
    
summary_id = fields.Many2one(
    'daily.sales.summary',
    string='ملخص المبيعات',
    required=True,
    ondelete='set null'  # أو 'restrict' حسب المطلوب
)

    payment_method_line_id = fields.Many2one(
        'account.payment.method.line',
        string='طريقة السداد',
        required=True
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='دفتر اليومية',
        required=True
    )
    amount = fields.Monetary(
        string='المبلغ',
        currency_field='company_currency_id'
    )
    company_currency_id = fields.Many2one(
        'res.currency',
        string='العملة',
        related='summary_id.company_currency_id'
    )
