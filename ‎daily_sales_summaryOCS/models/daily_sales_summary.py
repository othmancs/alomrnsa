# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta
from collections import defaultdict
import io
import xlsxwriter
import base64
from bs4 import BeautifulSoup
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


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
    branch_ids = fields.Many2many(
        'res.branch',
        string='الفروع',
        help='تصفية النتائج حسب الفروع المحددة'
    )
    company_currency_id = fields.Many2one(
        'res.currency', string='العملة',
        related='company_id.currency_id', store=True
    )

    # الحقول المحسوبة
    cash_sales = fields.Monetary(
        string='مبيعات نقدية مدفوعة بتاريخه قبل الضريبة',
        currency_field='company_currency_id',
        compute='_compute_sales_totals', store=True
    )
    total_tax = fields.Monetary(
        string='مجموع الضريبة فقط',
        currency_field='company_currency_id',
        compute='_compute_sales_totals', store=True
    )
    partial_sales = fields.Monetary(
        string='مبيعات مدفوع جزئي',
        currency_field='company_currency_id',
        compute='_compute_sales_totals', store=True
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
    payment_method_totals = fields.Html(
        string='المجاميع حسب طريقة الدفع',
        compute='_compute_payment_method_totals',
        sanitize=False
    )

    @api.depends('date_from', 'date_to', 'company_id', 'branch_ids')
    def _compute_payment_method_totals(self):
        for record in self:
            payment_method_data = defaultdict(float)

            cash_domain = [
                ('invoice_date', '>=', record.date_from),
                ('invoice_date', '<=', record.date_to),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', '=', 'paid'),
                ('company_id', '=', record.company_id.id)
            ]
            if record.branch_ids:
                cash_domain.append(('branch_id', 'in', record.branch_ids.ids))

            cash_invoices = self.env['account.move'].search(cash_domain)
            for invoice in cash_invoices:
                for payment in invoice._get_reconciled_payments():
                    if payment.payment_method_line_id:
                        method_name = payment.payment_method_line_id.name or 'غير محدد'
                        payment_method_data[method_name] += payment.amount

            # حساب المبيعات المدفوعة جزئياً حسب طريقة الدفع
            partial_domain = [
                ('invoice_date', '>=', record.date_from),
                ('invoice_date', '<=', record.date_to),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', '=', 'partial'),
                ('company_id', '=', record.company_id.id)
            ]
            if record.branch_ids:
                partial_domain.append(('branch_id', 'in', record.branch_ids.ids))

            partial_invoices = self.env['account.move'].search(partial_domain)
            for invoice in partial_invoices:
                for payment in invoice._get_reconciled_payments():
                    if payment.payment_method_line_id:
                        method_name = payment.payment_method_line_id.name or 'غير محدد'
                        payment_method_data[method_name] += payment.amount

            # حساب المقبوضات حسب طريقة الدفع
            payment_domain = [
                ('date', '>=', record.date_from),
                ('date', '<=', record.date_to),
                ('payment_type', '=', 'inbound'),
                ('state', '=', 'posted'),
                ('is_internal_transfer', '=', False),
                ('company_id', '=', record.company_id.id)
            ]
            if record.branch_ids:
                payment_domain.append(('branch_id', 'in', record.branch_ids.ids))

            payments = self.env['account.payment'].search(payment_domain)
            for payment in payments:
                if payment.payment_method_line_id:
                    method_name = payment.payment_method_line_id.name or 'غير محدد'
                    payment_method_data[method_name] += payment.amount

            # تحويل البيانات إلى نص لعرضها
            result = []
            for method, amount in sorted(payment_method_data.items()):
                if amount:
                    formatted_amount = format(amount, '.2f')
                    result.append(f"{method}: {formatted_amount} {record.company_currency_id.symbol}")

            record.payment_method_totals = "\n".join(result) if result else "لا توجد مدفوعات"

    @api.depends('date_from', 'date_to', 'company_id', 'branch_ids')
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
            if record.branch_ids:
                cash_domain.append(('branch_id', 'in', record.branch_ids.ids))
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
            if record.branch_ids:
                partial_domain.append(('branch_id', 'in', record.branch_ids.ids))
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
            if record.branch_ids:
                credit_domain.append(('branch_id', 'in', record.branch_ids.ids))
            credit_invoices = self.env['account.move'].search(credit_domain)
            record.credit_sales = sum(invoice.amount_untaxed for invoice in credit_invoices)

    @api.depends('date_from', 'date_to', 'company_id', 'branch_ids')
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
            if record.branch_ids:
                cash_refund_domain.append(('branch_id', 'in', record.branch_ids.ids))
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
            if record.branch_ids:
                credit_refund_domain.append(('branch_id', 'in', record.branch_ids.ids))
            credit_refunds = self.env['account.move'].search(credit_refund_domain)
            record.credit_refunds = sum(refund.amount_untaxed for refund in credit_refunds)

    @api.depends('date_from', 'date_to', 'company_id', 'branch_ids')
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
            if record.branch_ids:
                payment_domain.append(('branch_id', 'in', record.branch_ids.ids))
            payments = self.env['account.payment'].search(payment_domain)
            record.cash_box = sum(payment.amount for payment in payments)

    @api.depends('cash_sales', 'partial_sales', 'cash_refunds', 'cash_box')
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
        if self.branch_ids:
            domain.append(('branch_id', 'in', self.branch_ids.ids))
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
        if self.branch_ids:
            domain.append(('branch_id', 'in', self.branch_ids.ids))
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
        if self.branch_ids:
            domain.append(('branch_id', 'in', self.branch_ids.ids))
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
        if self.branch_ids:
            domain.append(('branch_id', 'in', self.branch_ids.ids))
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
        if self.branch_ids:
            domain.append(('branch_id', 'in', self.branch_ids.ids))
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
        if self.branch_ids:
            domain.append(('branch_id', 'in', self.branch_ids.ids))
        action['domain'] = domain
        action['context'] = {
            'default_payment_type': 'inbound',
            'create': False
        }
        return action

    @api.model
    def generate_sales_collection_report(self):
        """إنشاء تقرير Excel للمبيعات والتحصيل حسب الهيكل المطلوب"""
        # إنشاء كتاب Excel
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('المبيعات والتحصيل')
    
        # تنسيقات الخلايا
        title_format = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'font_size': 16, 'font_color': '#4472C4'
        })
        header_format = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'bg_color': '#4472C4', 'font_color': 'white', 'border': 1,
            'font_size': 12, 'text_wrap': True
        })
        currency_format = workbook.add_format({
            'num_format': '#,##0.00', 'border': 1, 'align': 'right'
        })
        text_format = workbook.add_format({'border': 1, 'align': 'right'})
        total_format = workbook.add_format({
            'bold': True, 'num_format': '#,##0.00', 'border': 1,
            'align': 'right', 'bg_color': '#D9E1F2'
        })
        branch_header_format = workbook.add_format({
            'bold': True, 'align': 'right', 'valign': 'vcenter',
            'bg_color': '#E2EFDA', 'font_color': 'black', 'border': 1,
            'font_size': 12
        })
    
        # إضافة عنوان التقرير
        row = 0
        worksheet.merge_range(row, 0, row, 12, 'تقرير المبيعات والتحصيل اليومي', title_format)
        row += 1
        worksheet.merge_range(row, 0, row, 12, f'من {self.date_from} إلى {self.date_to}', 
                             workbook.add_format({'align': 'center', 'font_size': 12}))
        row += 2
    
        # تحديد عرض الأعمدة
        worksheet.set_column(0, 0, 25)  # عمود الفرع
        worksheet.set_column(1, 12, 15)  # الأعمدة الرقمية
    
        # إنشاء صف العناوين الرئيسية
        headers = [
            'الفرع',
            'إجمالي المبيعات النقدية',
            'نقدي', 'شبكة', 'حوالة', 'طرق أخرى',  # تقسيم المدفوعات للمبيعات النقدية
            'إجمالي التحصيل الآجل',
            'نقدي', 'شبكة', 'حوالة', 'طرق أخرى',  # تقسيم المدفوعات للتحصيل الآجل
            'نقدي & التحصيل',
            'صافي الصندوق',
            'الارجاعات غير المستردة',
            'الارجاعات المستردة',
            'إجمالي المبيعات الآجلة',
            'إجمالي المبيعات'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(row, col, header, header_format)
        row += 1
    
        # جمع البيانات لكل فرع على حدة
        branch_ids = self.branch_ids.ids if self.branch_ids else self.env['res.branch'].search([]).ids
        branches = self.env['res.branch'].browse(branch_ids)
    
        # متغيرات لتخزين الإجماليات
        totals = {
            'cash_sales': 0,
            'cash_payments': defaultdict(float),
            'credit_collection': 0,
            'credit_payments': defaultdict(float),
            'cash_and_collection': 0,
            'net_cash': 0,
            'credit_refunds': 0,
            'cash_refunds': 0,
            'credit_sales': 0,
            'total_sales': 0
        }
    
        for branch in branches:
            # 1. حساب المبيعات النقدية (فواتير بنفس تاريخ التقرير ومدفوعة بالكامل في نفس التاريخ)
            cash_sales_domain = [
                ('invoice_date', '>=', self.date_from),
                ('invoice_date', '<=', self.date_to),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', '=', 'paid'),
                ('company_id', '=', self.company_id.id),
                ('branch_id', '=', branch.id)
            ]
            cash_invoices = self.env['account.move'].search(cash_sales_domain)
            branch_cash_sales = sum(invoice.amount_untaxed for invoice in cash_invoices)
            
            # تقسيم المدفوعات للمبيعات النقدية حسب نوع الدفع
            cash_payments = defaultdict(float)
            for invoice in cash_invoices:
                for payment in invoice._get_reconciled_payments():
                    if payment.payment_method_line_id:
                        method = payment.payment_method_line_id.name or 'طرق أخرى'
                        cash_payments[method] += payment.amount
    
            # 2. حساب التحصيل الآجل (مدفوعات لفواتير قديمة)
            credit_payments_domain = [
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
                ('payment_type', '=', 'inbound'),
                ('state', '=', 'posted'),
                ('is_internal_transfer', '=', False),
                ('company_id', '=', self.company_id.id),
                ('branch_id', '=', branch.id),
                ('reconciled_bill_ids', '!=', False)
            ]
            credit_payments = self.env['account.payment'].search(credit_payments_domain)
            
            # فلترة المدفوعات التي ليست للمبيعات النقدية
            branch_credit_collection = 0
            credit_payments_split = defaultdict(float)
            for payment in credit_payments:
                invoice_date = payment.reconciled_invoice_ids[0].invoice_date if payment.reconciled_invoice_ids else None
                if invoice_date and (invoice_date < self.date_from or invoice_date > self.date_to):
                    branch_credit_collection += payment.amount
                    method = payment.payment_method_line_id.name or 'طرق أخرى'
                    credit_payments_split[method] += payment.amount
    
            # 3. حساب نقدي & التحصيل
            branch_cash_and_collection = branch_cash_sales + branch_credit_collection
    
            # 4. حساب المرتجعات
            cash_refunds_domain = [
                ('invoice_date', '>=', self.date_from),
                ('invoice_date', '<=', self.date_to),
                ('move_type', '=', 'out_refund'),
                ('state', '=', 'posted'),
                ('payment_state', '=', 'paid'),
                ('company_id', '=', self.company_id.id),
                ('branch_id', '=', branch.id)
            ]
            cash_refunds = self.env['account.move'].search(cash_refunds_domain)
            branch_cash_refunds = sum(abs(refund.amount_untaxed) for refund in cash_refunds)
    
            credit_refunds_domain = [
                ('invoice_date', '>=', self.date_from),
                ('invoice_date', '<=', self.date_to),
                ('move_type', '=', 'out_refund'),
                ('state', '=', 'posted'),
                ('payment_state', '=', 'not_paid'),
                ('company_id', '=', self.company_id.id),
                ('branch_id', '=', branch.id)
            ]
            credit_refunds = self.env['account.move'].search(credit_refunds_domain)
            branch_credit_refunds = sum(abs(refund.amount_untaxed) for refund in credit_refunds)
    
            # 5. حساب صافي الصندوق
            branch_net_cash = branch_cash_and_collection - branch_cash_refunds
    
            # 6. حساب المبيعات الآجلة (فواتير بنفس تاريخ التقرير وغير مدفوعة)
            credit_sales_domain = [
                ('invoice_date', '>=', self.date_from),
                ('invoice_date', '<=', self.date_to),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', '=', 'not_paid'),
                ('company_id', '=', self.company_id.id),
                ('branch_id', '=', branch.id)
            ]
            credit_invoices = self.env['account.move'].search(credit_sales_domain)
            branch_credit_sales = sum(invoice.amount_untaxed for invoice in credit_invoices)
    
            # 7. إجمالي المبيعات
            branch_total_sales = branch_cash_sales + branch_credit_sales
    
            # كتابة بيانات الفرع
            col = 0
            worksheet.write(row, col, branch.name, branch_header_format); col += 1
            
            # إجمالي المبيعات النقدية
            worksheet.write(row, col, branch_cash_sales, currency_format); col += 1
            
            # تقسيم المدفوعات للمبيعات النقدية
            worksheet.write(row, col, cash_payments.get('نقدي', 0), currency_format); col += 1
            worksheet.write(row, col, cash_payments.get('شبكة', 0), currency_format); col += 1
            worksheet.write(row, col, cash_payments.get('حوالة', 0), currency_format); col += 1
            worksheet.write(row, col, branch_cash_sales - sum(cash_payments.values()), currency_format); col += 1
            
            # إجمالي التحصيل الآجل
            worksheet.write(row, col, branch_credit_collection, currency_format); col += 1
            
            # تقسيم المدفوعات للتحصيل الآجل
            worksheet.write(row, col, credit_payments_split.get('نقدي', 0), currency_format); col += 1
            worksheet.write(row, col, credit_payments_split.get('شبكة', 0), currency_format); col += 1
            worksheet.write(row, col, credit_payments_split.get('حوالة', 0), currency_format); col += 1
            worksheet.write(row, col, branch_credit_collection - sum(credit_payments_split.values()), currency_format); col += 1
            
            # نقدي & التحصيل
            worksheet.write(row, col, branch_cash_and_collection, currency_format); col += 1
            
            # صافي الصندوق
            worksheet.write(row, col, branch_net_cash, currency_format); col += 1
            
            # الإرجاعات غير المستردة
            worksheet.write(row, col, branch_credit_refunds, currency_format); col += 1
            
            # الإرجاعات المستردة
            worksheet.write(row, col, branch_cash_refunds, currency_format); col += 1
            
            # إجمالي المبيعات الآجلة
            worksheet.write(row, col, branch_credit_sales, currency_format); col += 1
            
            # إجمالي المبيعات
            worksheet.write(row, col, branch_total_sales, currency_format)
    
            # تحديث الإجماليات
            totals['cash_sales'] += branch_cash_sales
            for method, amount in cash_payments.items():
                totals['cash_payments'][method] += amount
            totals['credit_collection'] += branch_credit_collection
            for method, amount in credit_payments_split.items():
                totals['credit_payments'][method] += amount
            totals['cash_and_collection'] += branch_cash_and_collection
            totals['net_cash'] += branch_net_cash
            totals['credit_refunds'] += branch_credit_refunds
            totals['cash_refunds'] += branch_cash_refunds
            totals['credit_sales'] += branch_credit_sales
            totals['total_sales'] += branch_total_sales
    
            row += 1
    
        # إضافة المجموع الكلي
        if len(branches) > 1:
            col = 0
            worksheet.write(row, col, 'الإجمالي', header_format); col += 1
            
            worksheet.write(row, col, totals['cash_sales'], total_format); col += 1
            worksheet.write(row, col, totals['cash_payments'].get('نقدي', 0), total_format); col += 1
            worksheet.write(row, col, totals['cash_payments'].get('شبكة', 0), total_format); col += 1
            worksheet.write(row, col, totals['cash_payments'].get('حوالة', 0), total_format); col += 1
            worksheet.write(row, col, totals['cash_sales'] - sum(totals['cash_payments'].values()), total_format); col += 1
            
            worksheet.write(row, col, totals['credit_collection'], total_format); col += 1
            worksheet.write(row, col, totals['credit_payments'].get('نقدي', 0), total_format); col += 1
            worksheet.write(row, col, totals['credit_payments'].get('شبكة', 0), total_format); col += 1
            worksheet.write(row, col, totals['credit_payments'].get('حوالة', 0), total_format); col += 1
            worksheet.write(row, col, totals['credit_collection'] - sum(totals['credit_payments'].values()), total_format); col += 1
            
            worksheet.write(row, col, totals['cash_and_collection'], total_format); col += 1
            worksheet.write(row, col, totals['net_cash'], total_format); col += 1
            worksheet.write(row, col, totals['credit_refunds'], total_format); col += 1
            worksheet.write(row, col, totals['cash_refunds'], total_format); col += 1
            worksheet.write(row, col, totals['credit_sales'], total_format); col += 1
            worksheet.write(row, col, totals['total_sales'], total_format)
    
        # إغلاق الكتاب وحفظه
        workbook.close()
        output.seek(0)
    
        return {
            'file_name': f"تقرير_المبيعات_و_التحصيل_{self.date_from}_إلى_{self.date_to}.xlsx",
            'file_content': output.read(),
            'file_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
    def action_generate_excel_report(self):
        """إجراء لإنشاء وتنزيل التقرير"""
        self.ensure_one()
        try:
            report_data = self.generate_sales_collection_report()
            
            # إنشاء مرفق (attachment) للتقرير
            attachment = self.env['ir.attachment'].create({
                'name': report_data['file_name'],
                'datas': base64.b64encode(report_data['file_content']),
                'res_model': 'daily.sales.summary',
                'res_id': self.id,
                'type': 'binary'
            })
            
            # إرجاع إجراء لتنزيل المرفق
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s?download=true' % attachment.id,
                'target': 'self',
            }
        except Exception as e:
            _logger.error("Failed to generate sales report: %s", str(e))
            raise

    def _compute_total_cash_methods(self, summaries):
        """حساب إجمالي الكاش الوارد باستثناء طرق السداد المحددة"""
        total = 0.0
        excluded_methods = ['شبكة', 'حوالة']  # طرق السداد المستثناة

        for summary in summaries:
            # تحليل محتوى payment_method_totals
            if not summary.payment_method_totals:
                continue

            # تحليل HTML للحصول على طرق الدفع والمبالغ
            soup = BeautifulSoup(summary.payment_method_totals, 'html.parser')
            lines = soup.get_text().split('\n')

            for line in lines:
                if ':' in line:
                    method, amount = line.split(':', 1)
                    method = method.strip()
                    amount = amount.strip().split()[0]

                    # استبعاد طرق السداد المحددة
                    if not any(excluded in method for excluded in excluded_methods):
                        try:
                            total += float(amount.replace(',', ''))
                        except ValueError:
                            continue
        return total
