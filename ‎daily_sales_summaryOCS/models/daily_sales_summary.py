# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta
from collections import defaultdict
import io
import xlsxwriter
import base64
from bs4 import BeautifulSoup
from datetime import datetime


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

    def generate_sales_collection_report(self):
        """إنشاء تقرير Excel للمبيعات والتحصيل مع تفصيل طرق الدفع"""
        # إنشاء كتاب Excel
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('المبيعات والتحصيل')
    
        # تنسيقات الخلايا
        title_format = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'font_size': 16, 'font_color': '#4472C4'
        })
        subtitle_format = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter', 'font_size': 14
        })
        date_format = workbook.add_format({
            'align': 'center', 'valign': 'vcenter', 'font_size': 12
        })
        header_format = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'bg_color': '#4472C4', 'font_color': 'white', 'border': 1, 'font_size': 12, 'text_wrap': True
        })
        currency_format = workbook.add_format({
            'num_format': '#,##0.00', 'border': 1, 'align': 'right'
        })
        text_format = workbook.add_format({'border': 1, 'align': 'right'})
        total_format = workbook.add_format({
            'bold': True, 'num_format': '#,##0.00', 'border': 1,
            'align': 'right', 'bg_color': '#D9E1F2'
        })
    
        # كتابة عنوان التقرير
        worksheet.merge_range('A1:I1', self.company_id.name, title_format)
        worksheet.merge_range('A2:I2', 'تقرير حركة المبيعات اليومية', subtitle_format)
        worksheet.merge_range('A3:I3', f'من {self.date_from} إلى {self.date_to}', date_format)
        worksheet.write(3, 0, '', workbook.add_format())
    
        # الحصول على جميع طرق الدفع الفريدة المستخدمة في الفترة
        payment_methods = set()
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
        
        invoices = self.env['account.move'].search(domain)
        for invoice in invoices:
            for payment in invoice._get_reconciled_payments():
                if payment.payment_method_line_id:
                    payment_methods.add(payment.payment_method_line_id.name or 'غير محدد')
    
        # عناوين الأعمدة الجديدة المعدلة
        base_headers = [
            'الفرع',
            'المبيعات النقدية',  # (إجمالي المبيعات مع الضريبة)
            'صافي المبيعات الآجلة'
        ]
        
        # إضافة أعمدة لطرق الدفع الفريدة (لتحصيل النقدي)
        for method in sorted(payment_methods):
            base_headers.append(f'{method}')
        
        # إضافة الأعمدة المعدلة
        base_headers.extend([
            'التحصيل النقدي',
            'التحصيل الآجل',
            'إجمالي المقبوضات'
        ])
    
        # تحديد عرض الأعمدة
        worksheet.set_column(0, 0, 30)  # عمود الفرع
        worksheet.set_column(1, len(base_headers)-1, 20)  # الأعمدة الرقمية
    
        # كتابة العناوين
        for col, header in enumerate(base_headers):
            worksheet.write(4, col, header, header_format)
    
        # جمع البيانات لكل فرع على حدة
        branch_ids = self.branch_ids.ids if self.branch_ids else self.env['res.branch'].search([]).ids
        branches = self.env['res.branch'].browse(branch_ids)
    
        # متغيرات لتخزين الإجماليات
        totals = {
            'cash_sales': 0,
            'credit': 0,
            'cash_receipts': 0,
            'credit_receipts': 0,
            'total_receipts': 0
        }
        for method in payment_methods:
            totals[f'method_{method}'] = 0
    
        row = 5  # بدء البيانات من الصف 5 بعد العناوين
        for branch in branches:
            # حساب المبيعات النقدية للفرع
            cash_invoices = self.env['account.move'].search([
                ('invoice_date', '>=', self.date_from),
                ('invoice_date', '<=', self.date_to),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', '=', 'paid'),
                ('company_id', '=', self.company_id.id),
                ('branch_id', '=', branch.id)
            ])
            
            # حساب المبيعات حسب طريقة الدفع (مجمعة حسب الاسم)
            method_totals = {method: 0.0 for method in payment_methods}
            
            for invoice in cash_invoices:
                for payment in invoice._get_reconciled_payments():
                    if payment.payment_method_line_id:
                        method_name = payment.payment_method_line_id.name or 'غير محدد'
                        if method_name in method_totals:
                            method_totals[method_name] += payment.amount
            
            branch_cash_sales = sum(invoice.amount_total for invoice in cash_invoices)  # الإجمالي مع الضريبة
    
            # حساب المبيعات الآجلة للفرع
            credit_invoices = self.env['account.move'].search([
                ('invoice_date', '>=', self.date_from),
                ('invoice_date', '<=', self.date_to),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', '=', 'not_paid'),
                ('company_id', '=', self.company_id.id),
                ('branch_id', '=', branch.id)
            ])
            branch_credit = sum(invoice.amount_total for invoice in credit_invoices)  # الإجمالي مع الضريبة
    
            # حساب إرجاعات مسترد المبلغ للفرع
            cash_refunds = self.env['account.move'].search([
                ('invoice_date', '>=', self.date_from),
                ('invoice_date', '<=', self.date_to),
                ('move_type', '=', 'out_refund'),
                ('state', '=', 'posted'),
                ('payment_state', '=', 'paid'),
                ('company_id', '=', self.company_id.id),
                ('branch_id', '=', branch.id)
            ])
            branch_cash_refunds = sum(refund.amount_total for refund in cash_refunds)
    
            # حساب إجمالي المقبوضات (المدفوعات الواردة)
            payments = self.env['account.payment'].search([
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
                ('payment_type', '=', 'inbound'),
                ('state', '=', 'posted'),
                ('is_internal_transfer', '=', False),
                ('company_id', '=', self.company_id.id),
                ('branch_id', '=', branch.id)
            ])
            branch_total_receipts = sum(payment.amount for payment in payments) - branch_cash_refunds
    
            # التحصيل النقدي (إجمالي المبيعات النقدية)
            branch_cash_receipts = branch_cash_sales
    
            # التحصيل الآجل (إجمالي المقبوضات - التحصيل النقدي)
            branch_credit_receipts = branch_total_receipts - branch_cash_receipts
    
            # تحديث الإجماليات
            totals['cash_sales'] += branch_cash_sales
            totals['credit'] += branch_credit
            totals['cash_receipts'] += branch_cash_receipts
            totals['credit_receipts'] += branch_credit_receipts
            totals['total_receipts'] += branch_total_receipts
            
            for method, amount in method_totals.items():
                totals[f'method_{method}'] += amount
    
            # كتابة بيانات الفرع
            col = 0
            worksheet.write(row, col, branch.name, text_format); col += 1
            worksheet.write(row, col, branch_cash_sales, currency_format); col += 1
            worksheet.write(row, col, branch_credit, currency_format); col += 1
            
            # كتابة مبيعات كل طريقة دفع
            for method in sorted(payment_methods):
                worksheet.write(row, col, method_totals.get(method, 0.0), currency_format)
                col += 1
            
            worksheet.write(row, col, branch_cash_receipts, currency_format); col += 1
            worksheet.write(row, col, branch_credit_receipts, currency_format); col += 1
            worksheet.write(row, col, branch_total_receipts, currency_format)
    
            row += 1
    
        # إضافة المجموع الكلي إذا كان هناك أكثر من فرع
        if row > 5:
            col = 0
            worksheet.write(row, col, 'الإجمالي', header_format); col += 1
            worksheet.write(row, col, totals['cash_sales'], total_format); col += 1
            worksheet.write(row, col, totals['credit'], total_format); col += 1
            
            for method in sorted(payment_methods):
                worksheet.write(row, col, totals.get(f'method_{method}', 0.0), total_format)
                col += 1
            
            worksheet.write(row, col, totals['cash_receipts'], total_format); col += 1
            worksheet.write(row, col, totals['credit_receipts'], total_format); col += 1
            worksheet.write(row, col, totals['total_receipts'], total_format)
    
        # إغلاق الكتاب وحفظه
        workbook.close()
        output.seek(0)
    
        return {
            'file_name': f"تقرير_المبيعات_اليومية_{self.date_from}_إلى_{self.date_to}.xlsx",
            'file_content': output.read(),
            'file_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
    
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

    def action_generate_excel_report(self):
        """إجراء لإنشاء وتنزيل التقرير"""
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

# -*- coding: utf-8 -*-

# from odoo import models, fields, api
# from datetime import timedelta
# from collections import defaultdict
# import io
# import xlsxwriter
# import base64
# from bs4 import BeautifulSoup
# from datetime import datetime


# class DailySalesSummary(models.Model):
#     _name = 'daily.sales.summary'
#     _description = 'ملخص حركة المبيعات اليومية'
#     _rec_name = 'date_from'
#     _order = 'date_from desc'

#     date_from = fields.Date(string='من تاريخ', default=fields.Date.today(), required=True)
#     date_to = fields.Date(string='إلى تاريخ', default=fields.Date.today(), required=True)
#     company_id = fields.Many2one(
#         'res.company', string='الشركة',
#         default=lambda self: self.env.company, required=True
#     )
#     branch_ids = fields.Many2many(
#         'res.branch',
#         string='الفروع',
#         help='تصفية النتائج حسب الفروع المحددة'
#     )
#     company_currency_id = fields.Many2one(
#         'res.currency', string='العملة',
#         related='company_id.currency_id', store=True
#     )

#     # الحقول المحسوبة
#     cash_sales = fields.Monetary(
#         string='مبيعات نقدية مدفوعة بتاريخه قبل الضريبة',
#         currency_field='company_currency_id',
#         compute='_compute_sales_totals', store=True
#     )
#     total_tax = fields.Monetary(
#         string='مجموع الضريبة فقط',
#         currency_field='company_currency_id',
#         compute='_compute_sales_totals', store=True
#     )
#     partial_sales = fields.Monetary(
#         string='مبيعات مدفوع جزئي',
#         currency_field='company_currency_id',
#         compute='_compute_sales_totals', store=True
#     )
#     credit_sales = fields.Monetary(
#         string='مبيعات آجلة غير مدفوعة',
#         currency_field='company_currency_id',
#         compute='_compute_sales_totals', store=True
#     )
#     cash_refunds = fields.Monetary(
#         string='إرجاعات مسترد المبلغ',
#         currency_field='company_currency_id',
#         compute='_compute_refund_totals', store=True
#     )
#     credit_refunds = fields.Monetary(
#         string='إرجاعات غير مسترد المبلغ',
#         currency_field='company_currency_id',
#         compute='_compute_refund_totals', store=True
#     )
#     cash_box = fields.Monetary(
#         string='المقبوضات',
#         currency_field='company_currency_id',
#         compute='_compute_cash_box', store=True
#     )
#     total_cash = fields.Monetary(
#         string='إجمالي الصندوق',
#         currency_field='company_currency_id',
#         compute='_compute_total_cash', store=True
#     )
#     payment_method_totals = fields.Html(
#         string='المجاميع حسب طريقة الدفع',
#         compute='_compute_payment_method_totals',
#         sanitize=False
#     )

#     @api.depends('date_from', 'date_to', 'company_id', 'branch_ids')
#     def _compute_payment_method_totals(self):
#         for record in self:
#             payment_method_data = defaultdict(float)

#             cash_domain = [
#                 ('invoice_date', '>=', record.date_from),
#                 ('invoice_date', '<=', record.date_to),
#                 ('move_type', '=', 'out_invoice'),
#                 ('state', '=', 'posted'),
#                 ('payment_state', '=', 'paid'),
#                 ('company_id', '=', record.company_id.id)
#             ]
#             if record.branch_ids:
#                 cash_domain.append(('branch_id', 'in', record.branch_ids.ids))

#             cash_invoices = self.env['account.move'].search(cash_domain)
#             for invoice in cash_invoices:
#                 for payment in invoice._get_reconciled_payments():
#                     if payment.payment_method_line_id:
#                         method_name = payment.payment_method_line_id.name or 'غير محدد'
#                         payment_method_data[method_name] += payment.amount

#             # حساب المبيعات المدفوعة جزئياً حسب طريقة الدفع
#             partial_domain = [
#                 ('invoice_date', '>=', record.date_from),
#                 ('invoice_date', '<=', record.date_to),
#                 ('move_type', '=', 'out_invoice'),
#                 ('state', '=', 'posted'),
#                 ('payment_state', '=', 'partial'),
#                 ('company_id', '=', record.company_id.id)
#             ]
#             if record.branch_ids:
#                 partial_domain.append(('branch_id', 'in', record.branch_ids.ids))

#             partial_invoices = self.env['account.move'].search(partial_domain)
#             for invoice in partial_invoices:
#                 for payment in invoice._get_reconciled_payments():
#                     if payment.payment_method_line_id:
#                         method_name = payment.payment_method_line_id.name or 'غير محدد'
#                         payment_method_data[method_name] += payment.amount

#             # حساب المقبوضات حسب طريقة الدفع
#             payment_domain = [
#                 ('date', '>=', record.date_from),
#                 ('date', '<=', record.date_to),
#                 ('payment_type', '=', 'inbound'),
#                 ('state', '=', 'posted'),
#                 ('is_internal_transfer', '=', False),
#                 ('company_id', '=', record.company_id.id)
#             ]
#             if record.branch_ids:
#                 payment_domain.append(('branch_id', 'in', record.branch_ids.ids))

#             payments = self.env['account.payment'].search(payment_domain)
#             for payment in payments:
#                 if payment.payment_method_line_id:
#                     method_name = payment.payment_method_line_id.name or 'غير محدد'
#                     payment_method_data[method_name] += payment.amount

#             # تحويل البيانات إلى نص لعرضها
#             result = []
#             for method, amount in sorted(payment_method_data.items()):
#                 if amount:
#                     formatted_amount = format(amount, '.2f')
#                     result.append(f"{method}: {formatted_amount} {record.company_currency_id.symbol}")

#             record.payment_method_totals = "\n".join(result) if result else "لا توجد مدفوعات"

#     @api.depends('date_from', 'date_to', 'company_id', 'branch_ids')
#     def _compute_sales_totals(self):
#         for record in self:
#             # حساب المبيعات النقدية (مدفوع بالكامل في نفس التاريخ)
#             cash_domain = [
#                 ('invoice_date', '>=', record.date_from),
#                 ('invoice_date', '<=', record.date_to),
#                 ('move_type', '=', 'out_invoice'),
#                 ('state', '=', 'posted'),
#                 ('payment_state', '=', 'paid'),
#                 ('company_id', '=', record.company_id.id)
#             ]
#             if record.branch_ids:
#                 cash_domain.append(('branch_id', 'in', record.branch_ids.ids))
#             cash_invoices = self.env['account.move'].search(cash_domain)
#             record.cash_sales = sum(invoice.amount_untaxed for invoice in cash_invoices)
#             record.total_tax = sum(invoice.amount_tax for invoice in cash_invoices)

#             # حساب المبيعات المدفوعة جزئياً (نعرض المبلغ المدفوع فقط)
#             partial_domain = [
#                 ('invoice_date', '>=', record.date_from),
#                 ('invoice_date', '<=', record.date_to),
#                 ('move_type', '=', 'out_invoice'),
#                 ('state', '=', 'posted'),
#                 ('payment_state', '=', 'partial'),
#                 ('company_id', '=', record.company_id.id)
#             ]
#             if record.branch_ids:
#                 partial_domain.append(('branch_id', 'in', record.branch_ids.ids))
#             partial_invoices = self.env['account.move'].search(partial_domain)
#             record.partial_sales = sum(invoice.amount_total - invoice.amount_residual for invoice in partial_invoices)

#             # حساب المبيعات الآجلة (غير مدفوع)
#             credit_domain = [
#                 ('invoice_date', '>=', record.date_from),
#                 ('invoice_date', '<=', record.date_to),
#                 ('move_type', '=', 'out_invoice'),
#                 ('state', '=', 'posted'),
#                 ('payment_state', '=', 'not_paid'),
#                 ('company_id', '=', record.company_id.id)
#             ]
#             if record.branch_ids:
#                 credit_domain.append(('branch_id', 'in', record.branch_ids.ids))
#             credit_invoices = self.env['account.move'].search(credit_domain)
#             record.credit_sales = sum(invoice.amount_untaxed for invoice in credit_invoices)

#     @api.depends('date_from', 'date_to', 'company_id', 'branch_ids')
#     def _compute_refund_totals(self):
#         for record in self:
#             # حساب المرتجعات النقدية (مدفوع)
#             cash_refund_domain = [
#                 ('invoice_date', '>=', record.date_from),
#                 ('invoice_date', '<=', record.date_to),
#                 ('move_type', '=', 'out_refund'),
#                 ('state', '=', 'posted'),
#                 ('payment_state', '=', 'paid'),
#                 ('company_id', '=', record.company_id.id)
#             ]
#             if record.branch_ids:
#                 cash_refund_domain.append(('branch_id', 'in', record.branch_ids.ids))
#             cash_refunds = self.env['account.move'].search(cash_refund_domain)
#             record.cash_refunds = sum(refund.amount_untaxed for refund in cash_refunds)

#             # حساب مرتجعات الآجل (غير مدفوع)
#             credit_refund_domain = [
#                 ('invoice_date', '>=', record.date_from),
#                 ('invoice_date', '<=', record.date_to),
#                 ('move_type', '=', 'out_refund'),
#                 ('state', '=', 'posted'),
#                 ('payment_state', '=', 'not_paid'),
#                 ('company_id', '=', record.company_id.id)
#             ]
#             if record.branch_ids:
#                 credit_refund_domain.append(('branch_id', 'in', record.branch_ids.ids))
#             credit_refunds = self.env['account.move'].search(credit_refund_domain)
#             record.credit_refunds = sum(refund.amount_untaxed for refund in credit_refunds)

#     @api.depends('date_from', 'date_to', 'company_id', 'branch_ids')
#     def _compute_cash_box(self):
#         for record in self:
#             # حساب المقبوضات (الدفعات)
#             payment_domain = [
#                 ('date', '>=', record.date_from),
#                 ('date', '<=', record.date_to),
#                 ('payment_type', '=', 'inbound'),
#                 ('state', '=', 'posted'),
#                 ('is_internal_transfer', '=', False),
#                 ('company_id', '=', record.company_id.id)
#             ]
#             if record.branch_ids:
#                 payment_domain.append(('branch_id', 'in', record.branch_ids.ids))
#             payments = self.env['account.payment'].search(payment_domain)
#             record.cash_box = sum(payment.amount for payment in payments)

#     @api.depends('cash_sales', 'partial_sales', 'cash_refunds', 'cash_box')
#     def _compute_total_cash(self):
#         for record in self:
#             record.total_cash = record.cash_box - record.cash_refunds

#     @api.onchange('date_from')
#     def _onchange_date_from(self):
#         if self.date_from and not self.date_to:
#             self.date_to = self.date_from

#     @api.constrains('date_from', 'date_to')
#     def _check_dates(self):
#         for record in self:
#             if record.date_from and record.date_to and record.date_from > record.date_to:
#                 raise models.ValidationError("تاريخ البداية يجب أن يكون قبل تاريخ النهاية")

#     def action_view_cash_sales(self):
#         self.ensure_one()
#         action = self.env.ref('account.action_move_out_invoice_type').read()[0]
#         domain = [
#             ('invoice_date', '>=', self.date_from),
#             ('invoice_date', '<=', self.date_to),
#             ('move_type', '=', 'out_invoice'),
#             ('state', '=', 'posted'),
#             ('payment_state', '=', 'paid'),
#             ('company_id', '=', self.company_id.id)
#         ]
#         if self.branch_ids:
#             domain.append(('branch_id', 'in', self.branch_ids.ids))
#         action['domain'] = domain
#         action['context'] = {
#             'search_default_invoice': 1,
#             'create': False
#         }
#         return action

#     def action_view_partial_sales(self):
#         self.ensure_one()
#         action = self.env.ref('account.action_move_out_invoice_type').read()[0]
#         domain = [
#             ('invoice_date', '>=', self.date_from),
#             ('invoice_date', '<=', self.date_to),
#             ('move_type', '=', 'out_invoice'),
#             ('state', '=', 'posted'),
#             ('payment_state', '=', 'partial'),
#             ('company_id', '=', self.company_id.id)
#         ]
#         if self.branch_ids:
#             domain.append(('branch_id', 'in', self.branch_ids.ids))
#         action['domain'] = domain
#         action['context'] = {
#             'search_default_invoice': 1,
#             'create': False
#         }
#         return action

#     def action_view_credit_sales(self):
#         self.ensure_one()
#         action = self.env.ref('account.action_move_out_invoice_type').read()[0]
#         domain = [
#             ('invoice_date', '>=', self.date_from),
#             ('invoice_date', '<=', self.date_to),
#             ('move_type', '=', 'out_invoice'),
#             ('state', '=', 'posted'),
#             ('payment_state', '=', 'not_paid'),
#             ('company_id', '=', self.company_id.id)
#         ]
#         if self.branch_ids:
#             domain.append(('branch_id', 'in', self.branch_ids.ids))
#         action['domain'] = domain
#         action['context'] = {
#             'search_default_invoice': 1,
#             'create': False
#         }
#         return action

#     def action_view_cash_refunds(self):
#         self.ensure_one()
#         action = self.env.ref('account.action_move_out_refund_type').read()[0]
#         domain = [
#             ('invoice_date', '>=', self.date_from),
#             ('invoice_date', '<=', self.date_to),
#             ('move_type', '=', 'out_refund'),
#             ('state', '=', 'posted'),
#             ('payment_state', '=', 'paid'),
#             ('company_id', '=', self.company_id.id)
#         ]
#         if self.branch_ids:
#             domain.append(('branch_id', 'in', self.branch_ids.ids))
#         action['domain'] = domain
#         action['context'] = {
#             'search_default_refund': 1,
#             'create': False
#         }
#         return action

#     def action_view_credit_refunds(self):
#         self.ensure_one()
#         action = self.env.ref('account.action_move_out_refund_type').read()[0]
#         domain = [
#             ('invoice_date', '>=', self.date_from),
#             ('invoice_date', '<=', self.date_to),
#             ('move_type', '=', 'out_refund'),
#             ('state', '=', 'posted'),
#             ('payment_state', '=', 'not_paid'),
#             ('company_id', '=', self.company_id.id)
#         ]
#         if self.branch_ids:
#             domain.append(('branch_id', 'in', self.branch_ids.ids))
#         action['domain'] = domain
#         action['context'] = {
#             'search_default_refund': 1,
#             'create': False
#         }
#         return action

#     def action_view_cash_box(self):
#         self.ensure_one()
#         action = self.env.ref('account.action_account_payments').read()[0]
#         domain = [
#             ('date', '>=', self.date_from),
#             ('date', '<=', self.date_to),
#             ('payment_type', '=', 'inbound'),
#             ('state', '=', 'posted'),
#             ('is_internal_transfer', '=', False),
#             ('company_id', '=', self.company_id.id)
#         ]
#         if self.branch_ids:
#             domain.append(('branch_id', 'in', self.branch_ids.ids))
#         action['domain'] = domain
#         action['context'] = {
#             'default_payment_type': 'inbound',
#             'create': False
#         }
#         return action

#     def generate_sales_collection_report(self):
#         """إنشاء تقرير Excel للمبيعات والتحصيل مع تفصيل طرق الدفع"""
#         # إنشاء كتاب Excel
#         output = io.BytesIO()
#         workbook = xlsxwriter.Workbook(output, {'in_memory': True})
#         worksheet = workbook.add_worksheet('المبيعات والتحصيل')
    
#         # تنسيقات الخلايا
#         title_format = workbook.add_format({
#             'bold': True, 'align': 'center', 'valign': 'vcenter',
#             'font_size': 16, 'font_color': '#4472C4'
#         })
#         subtitle_format = workbook.add_format({
#             'bold': True, 'align': 'center', 'valign': 'vcenter', 'font_size': 14
#         })
#         date_format = workbook.add_format({
#             'align': 'center', 'valign': 'vcenter', 'font_size': 12
#         })
#         header_format = workbook.add_format({
#             'bold': True, 'align': 'center', 'valign': 'vcenter',
#             'bg_color': '#4472C4', 'font_color': 'white', 'border': 1, 'font_size': 12, 'text_wrap': True
#         })
#         currency_format = workbook.add_format({
#             'num_format': '#,##0.00', 'border': 1, 'align': 'right'
#         })
#         text_format = workbook.add_format({'border': 1, 'align': 'right'})
#         total_format = workbook.add_format({
#             'bold': True, 'num_format': '#,##0.00', 'border': 1,
#             'align': 'right', 'bg_color': '#D9E1F2'
#         })
    
#         # كتابة عنوان التقرير
#         worksheet.merge_range('A1:I1', self.company_id.name, title_format)
#         worksheet.merge_range('A2:I2', 'تقرير حركة المبيعات اليومية', subtitle_format)
#         worksheet.merge_range('A3:I3', f'من {self.date_from} إلى {self.date_to}', date_format)
#         worksheet.write(3, 0, '', workbook.add_format())
    
#         # الحصول على جميع طرق الدفع الفريدة المستخدمة في الفترة
#         payment_methods = set()
#         domain = [
#             ('invoice_date', '>=', self.date_from),
#             ('invoice_date', '<=', self.date_to),
#             ('move_type', '=', 'out_invoice'),
#             ('state', '=', 'posted'),
#             ('payment_state', '=', 'paid'),
#             ('company_id', '=', self.company_id.id)
#         ]
#         if self.branch_ids:
#             domain.append(('branch_id', 'in', self.branch_ids.ids))
        
#         invoices = self.env['account.move'].search(domain)
#         for invoice in invoices:
#             for payment in invoice._get_reconciled_payments():
#                 if payment.payment_method_line_id:
#                     payment_methods.add(payment.payment_method_line_id.name or 'غير محدد')
    
#         # عناوين الأعمدة الأساسية المعدلة
#         base_headers = [
#             'الفرع',
#             'إجمالي المبيعات النقدية (قبل الضريبة)',
#             'الضريبة',
#             'إجمالي المبيعات النقدية مع الضريبة'
#         ]
        
#         # إضافة أعمدة لطرق الدفع الفريدة
#         payment_methods = sorted(payment_methods)
#         for method in payment_methods:
#             base_headers.append(f'{method}')
        
#         # إضافة الأعمدة المعدلة
#         base_headers.extend([
#             'إجمالي المقبوضات',
#             'مقبوضات',
#             'صافي المبيعات الآجلة',
#             'إجمالي المبيعات'
#         ])
    
#         # تحديد عرض الأعمدة
#         worksheet.set_column(0, 0, 30)  # عمود الفرع
#         worksheet.set_column(1, len(base_headers)-1, 20)  # الأعمدة الرقمية
    
#         # كتابة العناوين
#         for col, header in enumerate(base_headers):
#             worksheet.write(4, col, header, header_format)
    
#         # جمع البيانات لكل فرع على حدة
#         branch_ids = self.branch_ids.ids if self.branch_ids else self.env['res.branch'].search([]).ids
#         branches = self.env['res.branch'].browse(branch_ids)
    
#         # متغيرات لتخزين الإجماليات
#         totals = {
#             'cash_sales': 0,
#             'tax': 0,
#             'cash_with_tax': 0,
#             'total_receipts': 0,
#             'sales_to_receipts': 0,
#             'credit': 0,
#             'total_sales': 0
#         }
#         for method in payment_methods:
#             totals[f'method_{method}'] = 0
    
#         row = 5  # بدء البيانات من الصف 5 بعد العناوين
#         for branch in branches:
#             # حساب المبيعات النقدية للفرع
#             cash_invoices = self.env['account.move'].search([
#                 ('invoice_date', '>=', self.date_from),
#                 ('invoice_date', '<=', self.date_to),
#                 ('move_type', '=', 'out_invoice'),
#                 ('state', '=', 'posted'),
#                 ('payment_state', '=', 'paid'),
#                 ('company_id', '=', self.company_id.id),
#                 ('branch_id', '=', branch.id)
#             ])
            
#             # حساب المبيعات حسب طريقة الدفع (مجمعة حسب الاسم)
#             method_totals = {method: 0.0 for method in payment_methods}
            
#             for invoice in cash_invoices:
#                 for payment in invoice._get_reconciled_payments():
#                     if payment.payment_method_line_id:
#                         method_name = payment.payment_method_line_id.name or 'غير محدد'
#                         if method_name in method_totals:
#                             method_totals[method_name] += payment.amount
            
#             branch_cash_sales = sum(invoice.amount_untaxed for invoice in cash_invoices)
#             branch_tax = sum(invoice.amount_tax for invoice in cash_invoices)
#             branch_cash_with_tax = branch_cash_sales + branch_tax
    
#             # حساب المبيعات المدفوعة جزئياً للفرع
#             partial_invoices = self.env['account.move'].search([
#                 ('invoice_date', '>=', self.date_from),
#                 ('invoice_date', '<=', self.date_to),
#                 ('move_type', '=', 'out_invoice'),
#                 ('state', '=', 'posted'),
#                 ('payment_state', '=', 'partial'),
#                 ('company_id', '=', self.company_id.id),
#                 ('branch_id', '=', branch.id)
#             ])
#             branch_partial_sales = sum(invoice.amount_total - invoice.amount_residual for invoice in partial_invoices)
    
#             # حساب إرجاعات مسترد المبلغ للفرع
#             cash_refunds = self.env['account.move'].search([
#                 ('invoice_date', '>=', self.date_from),
#                 ('invoice_date', '<=', self.date_to),
#                 ('move_type', '=', 'out_refund'),
#                 ('state', '=', 'posted'),
#                 ('payment_state', '=', 'paid'),
#                 ('company_id', '=', self.company_id.id),
#                 ('branch_id', '=', branch.id)
#             ])
#             branch_cash_refunds = sum(refund.amount_total for refund in cash_refunds)
    
#             # حساب إجمالي المقبوضات (المعادلة الجديدة)
#             payments = self.env['account.payment'].search([
#                 ('date', '>=', self.date_from),
#                 ('date', '<=', self.date_to),
#                 ('payment_type', '=', 'inbound'),
#                 ('state', '=', 'posted'),
#                 ('is_internal_transfer', '=', False),
#                 ('company_id', '=', self.company_id.id),
#                 ('branch_id', '=', branch.id)
#             ])
#             branch_total_receipts = sum(payment.amount for payment in payments) - branch_cash_refunds 
    
#             # حساب إجمالي المبيعات إلى مقبوضات الفرع (المعادلة الجديدة)
#             branch_sales_to_receipts = abs(branch_total_receipts - branch_cash_with_tax)
    
#             # حساب المبيعات الآجلة للفرع
#             credit_invoices = self.env['account.move'].search([
#                 ('invoice_date', '>=', self.date_from),
#                 ('invoice_date', '<=', self.date_to),
#                 ('move_type', '=', 'out_invoice'),
#                 ('state', '=', 'posted'),
#                 ('payment_state', '=', 'not_paid'),
#                 ('company_id', '=', self.company_id.id),
#                 ('branch_id', '=', branch.id)
#             ])
#             branch_credit = sum(invoice.amount_untaxed for invoice in credit_invoices)
    
#             # إجمالي المبيعات للفرع
#             branch_total = branch_cash_with_tax + branch_credit
    
#             # تحديث الإجماليات
#             totals['cash_sales'] += branch_cash_sales
#             totals['tax'] += branch_tax
#             totals['cash_with_tax'] += branch_cash_with_tax
#             totals['total_receipts'] += branch_total_receipts
#             totals['sales_to_receipts'] += branch_sales_to_receipts
#             totals['credit'] += branch_credit
#             totals['total_sales'] += branch_total
            
#             for method, amount in method_totals.items():
#                 totals[f'method_{method}'] += amount
    
#             # كتابة بيانات الفرع
#             col = 0
#             worksheet.write(row, col, branch.name, text_format); col += 1
#             worksheet.write(row, col, branch_cash_sales, currency_format); col += 1
#             worksheet.write(row, col, branch_tax, currency_format); col += 1
#             worksheet.write(row, col, branch_cash_with_tax, currency_format); col += 1
            
#             # كتابة مبيعات كل طريقة دفع
#             for method in payment_methods:
#                 worksheet.write(row, col, method_totals.get(method, 0.0), currency_format)
#                 col += 1
            
#             worksheet.write(row, col, branch_total_receipts, currency_format); col += 1
#             worksheet.write(row, col, branch_sales_to_receipts, currency_format); col += 1
#             worksheet.write(row, col, branch_credit, currency_format); col += 1
#             worksheet.write(row, col, branch_total, currency_format)
    
#             row += 1
    
#         # إضافة المجموع الكلي إذا كان هناك أكثر من فرع
#         if row > 5:
#             col = 0
#             worksheet.write(row, col, 'الإجمالي', header_format); col += 1
#             worksheet.write(row, col, totals['cash_sales'], total_format); col += 1
#             worksheet.write(row, col, totals['tax'], total_format); col += 1
#             worksheet.write(row, col, totals['cash_with_tax'], total_format); col += 1
            
#             for method in payment_methods:
#                 worksheet.write(row, col, totals.get(f'method_{method}', 0.0), total_format)
#                 col += 1
            
#             worksheet.write(row, col, totals['total_receipts'], total_format); col += 1
#             worksheet.write(row, col, totals['sales_to_receipts'], total_format); col += 1
#             worksheet.write(row, col, totals['credit'], total_format); col += 1
#             worksheet.write(row, col, totals['total_sales'], total_format)
    
#         # إغلاق الكتاب وحفظه
#         workbook.close()
#         output.seek(0)
    
#         return {
#             'file_name': f"تقرير_المبيعات_اليومية_{self.date_from}_إلى_{self.date_to}.xlsx",
#             'file_content': output.read(),
#             'file_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#         }
    
        
    
    
#     def _compute_total_cash_methods(self, summaries):
#         """حساب إجمالي الكاش الوارد باستثناء طرق السداد المحددة"""
#         total = 0.0
#         excluded_methods = ['شبكة', 'حوالة']  # طرق السداد المستثناة

#         for summary in summaries:
#             # تحليل محتوى payment_method_totals
#             if not summary.payment_method_totals:
#                 continue

#             # تحليل HTML للحصول على طرق الدفع والمبالغ
#             soup = BeautifulSoup(summary.payment_method_totals, 'html.parser')
#             lines = soup.get_text().split('\n')

#             for line in lines:
#                 if ':' in line:
#                     method, amount = line.split(':', 1)
#                     method = method.strip()
#                     amount = amount.strip().split()[0]

#                     # استبعاد طرق السداد المحددة
#                     if not any(excluded in method for excluded in excluded_methods):
#                         try:
#                             total += float(amount.replace(',', ''))
#                         except ValueError:
#                             continue
#         return total

#     def action_generate_excel_report(self):
#         """إجراء لإنشاء وتنزيل التقرير"""
#         report_data = self.generate_sales_collection_report()
        
#         # إنشاء مرفق (attachment) للتقرير
#         attachment = self.env['ir.attachment'].create({
#             'name': report_data['file_name'],
#             'datas': base64.b64encode(report_data['file_content']),
#             'res_model': 'daily.sales.summary',
#             'res_id': self.id,
#             'type': 'binary'
#         })
        
#         # إرجاع إجراء لتنزيل المرفق
#         return {
#             'type': 'ir.actions.act_url',
#             'url': '/web/content/%s?download=true' % attachment.id,
#             'target': 'self',
#         }
