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
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display

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
        workbook = xlsxwriter.Workbook(output, {'in_memory': True,'right_to_left': False})
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
        merged_header_format = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'bg_color': '#FFE699', 'font_color': 'black', 'border': 1,
            'font_size': 12
        })
    
        # إضافة شعار الشركة
        row = 0
        if self.company_id.logo:
            try:
                # إضافة الصورة بحجم مناسب (عرض 200 بكسل مع الحفاظ على النسبة)
                image_data = io.BytesIO(base64.b64decode(self.company_id.logo))
                worksheet.merge_range(row, 5, row+1, 5, '')  # دمج الخلايا لإنشاء مساحة للصورة
                worksheet.insert_image(row, 5, 'logo.png', {
                    'image_data': image_data,
                    'x_scale': 0.15, 
                    'y_scale': 0.15,
                    'x_offset': 10, 
                    'y_offset': 10,
                    'object_position': 3,  # 3 يعني أن الصورة ستتحرك مع الخلايا ولكن يمكن وضعها بحرية
                    'positioning': 1  # 1 يعني تحريك الخلايا لأسفل عند إدراج الصورة
                })
                # تحديد ارتفاع الصف ليتناسب مع الصورة
                worksheet.set_row(row, 80)  # ارتفاع 80 بكسل
                row += 1  # الانتقال إلى الصف التالي بعد الصورة
                
                # إضافة سطر فارغ لمنع تداخل الشعار مع النص
                worksheet.set_row(row, 15)  # سطر فارغ بارتفاع 15 بكسل
                row += 1
            except Exception as e:
                _logger.error(f"Failed to insert company logo: {str(e)}")
                # في حالة حدوث خطأ، نتابع بدون الصورة
                pass
    
        # إضافة عنوان التقرير
        worksheet.merge_range(row, 0, row, 11, 'تقرير المبيعات والتحصيل اليومي', title_format)
        row += 1
        worksheet.merge_range(row, 0, row, 11, f'من {self.date_from} إلى {self.date_to}', 
                             workbook.add_format({'align': 'center', 'font_size': 12}))
        row += 2
    
        # إنشاء صف العناوين الرئيسية
        headers = [
            'الفرع',
            'إجمالي المبيعات النقدية',
            'نقدي', 'شبكة', 'حوالة',  # تقسيم المدفوعات للمبيعات النقدية
            'إجمالي التحصيل الآجل',
            'نقدي', 'شبكة', 'حوالة',  # تقسيم المدفوعات للتحصيل الآجل
            'نقدي & التحصيل',
            'صافي الصندوق',
            'الارجاعات غير المستردة',
            'الارجاعات المستردة',
            'إجمالي المبيعات الآجلة',
            'إجمالي المبيعات'
        ]
        
        # إضافة صفوف العناوين المدمجة
        # الصف الأول: العناوين المدمجة
        worksheet.merge_range(row, 1, row, 4, 'المبيعات النقدية ونوع سدادها', merged_header_format)
        worksheet.merge_range(row, 5, row, 8, 'اجمالي التحصيل الآجل ونوع سدادها', merged_header_format)
        worksheet.merge_range(row, 9, row, 10, 'اجمالي المقبوضات', merged_header_format)
        worksheet.merge_range(row, 11, row, 12, 'الارجاعات', merged_header_format)
        worksheet.merge_range(row, 13, row, 14, 'الاجماليات', merged_header_format)
        row += 1
        
        # الصف الثاني: العناوين التفصيلية
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
            'total_sales': 0,
            'total_payments': 0,  # إجمالي جميع الدفعات
            'payment_methods': defaultdict(float)  # لتخزين طرق الدفع
        }
    
        # قائمة لتخزين أطوال المحتوى في كل عمود
        col_widths = [0] * len(headers)
        
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
                        method = payment.payment_method_line_id.name or 'نقدي'
                        # نحدد فقط الأنواع المطلوبة (نقدي، شبكة، حوالة)
                        if 'شبكة' in method:
                            method = 'شبكة'
                        elif 'حوالة' in method or 'شيك' in method:
                            method = 'حوالة'
                        else:
                            method = 'نقدي'
                        cash_payments[method] += payment.amount
                        totals['payment_methods'][method] += payment.amount
    
            # 2. حساب إجمالي جميع الدفعات (لحساب التحصيل الآجل)
            all_payments_domain = [
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
                ('payment_type', '=', 'inbound'),
                ('state', '=', 'posted'),
                ('is_internal_transfer', '=', False),
                ('company_id', '=', self.company_id.id),
                ('branch_id', '=', branch.id)
            ]
            all_payments = self.env['account.payment'].search(all_payments_domain)
            branch_total_payments = sum(payment.amount for payment in all_payments)
            
            # 3. حساب التحصيل الآجل (إجمالي الدفعات - المبيعات النقدية)
            branch_credit_collection = branch_total_payments - sum(cash_payments.values())
    
            # 4. تقسيم مدفوعات التحصيل الآجل حسب نوع الدفع
            credit_payments_split = defaultdict(float)
            for payment in all_payments:
                # نتأكد أن هذه الدفعة ليست من المبيعات النقدية
                is_cash_payment = False
                for invoice in payment.reconciled_invoice_ids:
                    if invoice.invoice_date and (self.date_from <= invoice.invoice_date <= self.date_to):
                        is_cash_payment = True
                        break
                
                if not is_cash_payment:
                    if payment.payment_method_line_id:
                        method = payment.payment_method_line_id.name or 'نقدي'
                        # نحدد فقط الأنواع المطلوبة (نقدي، شبكة، حوالة)
                        if 'شبكة' in method:
                            method = 'شبكة'
                        elif 'حوالة' in method or 'شيك' in method:
                            method = 'حوالة'
                        else:
                            method = 'نقدي'
                        credit_payments_split[method] += payment.amount
                        totals['payment_methods'][method] += payment.amount
    
            # 5. حساب نقدي & التحصيل
            branch_cash_and_collection = branch_cash_sales + branch_credit_collection
    
            # 6. حساب المرتجعات
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
    
            # 7. حساب صافي الصندوق
            branch_net_cash = branch_cash_and_collection - branch_cash_refunds
    
            # 8. حساب المبيعات الآجلة (فواتير بنفس تاريخ التقرير وغير مدفوعة)
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
    
            # 9. إجمالي المبيعات
            branch_total_sales = branch_cash_sales + branch_credit_sales
    
            # كتابة بيانات الفرع
            col = 0
            branch_name = branch.name or ''
            worksheet.write(row, col, branch_name, branch_header_format)
            col_widths[col] = max(col_widths[col], len(branch_name.encode('utf-8')))
            col += 1
            
            # إجمالي المبيعات النقدية
            cash_sales_str = f"{branch_cash_sales:,.2f}"
            worksheet.write(row, col, branch_cash_sales, currency_format)
            col_widths[col] = max(col_widths[col], len(cash_sales_str))
            col += 1
            
            # تقسيم المدفوعات للمبيعات النقدية (بدون عمود طرق أخرى)
            for method in ['نقدي', 'شبكة', 'حوالة']:
                amount = cash_payments.get(method, 0)
                amount_str = f"{amount:,.2f}"
                worksheet.write(row, col, amount, currency_format)
                col_widths[col] = max(col_widths[col], len(amount_str))
                col += 1
            
            # إجمالي التحصيل الآجل (مجموع الدفعات - المبيعات النقدية)
            credit_collection_str = f"{branch_credit_collection:,.2f}"
            worksheet.write(row, col, branch_credit_collection, currency_format)
            col_widths[col] = max(col_widths[col], len(credit_collection_str))
            col += 1
            
            # تقسيم المدفوعات للتحصيل الآجل (بدون عمود طرق أخرى)
            for method in ['نقدي', 'شبكة', 'حوالة']:
                amount = credit_payments_split.get(method, 0)
                amount_str = f"{amount:,.2f}"
                worksheet.write(row, col, amount, currency_format)
                col_widths[col] = max(col_widths[col], len(amount_str))
                col += 1
            
            # نقدي & التحصيل
            cash_collection_str = f"{branch_cash_and_collection:,.2f}"
            worksheet.write(row, col, branch_cash_and_collection, currency_format)
            col_widths[col] = max(col_widths[col], len(cash_collection_str))
            col += 1
            
            # صافي الصندوق
            net_cash_str = f"{branch_net_cash:,.2f}"
            worksheet.write(row, col, branch_net_cash, currency_format)
            col_widths[col] = max(col_widths[col], len(net_cash_str))
            col += 1
            
            # الإرجاعات غير المستردة
            credit_refunds_str = f"{branch_credit_refunds:,.2f}"
            worksheet.write(row, col, branch_credit_refunds, currency_format)
            col_widths[col] = max(col_widths[col], len(credit_refunds_str))
            col += 1
            
            # الإرجاعات المستردة
            cash_refunds_str = f"{branch_cash_refunds:,.2f}"
            worksheet.write(row, col, branch_cash_refunds, currency_format)
            col_widths[col] = max(col_widths[col], len(cash_refunds_str))
            col += 1
            
            # إجمالي المبيعات الآجلة
            credit_sales_str = f"{branch_credit_sales:,.2f}"
            worksheet.write(row, col, branch_credit_sales, currency_format)
            col_widths[col] = max(col_widths[col], len(credit_sales_str))
            col += 1
            
            # إجمالي المبيعات
            total_sales_str = f"{branch_total_sales:,.2f}"
            worksheet.write(row, col, branch_total_sales, currency_format)
            col_widths[col] = max(col_widths[col], len(total_sales_str))
    
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
            totals['total_payments'] += branch_total_payments
    
            row += 1
    
        # ضبط عرض الأعمدة حسب المحتوى
        for col, width in enumerate(col_widths):
            # تحويل طول المحتوى إلى عرض العمود (تقريبياً)
            # نضيف 2 للهامش ونضرب في 1.2 لتحويل الأحرف إلى وحدات عرض
            adjusted_width = (width + 2) * 1.2
            # نحدد حداً أدنى وأقصى لعرض العمود
            adjusted_width = max(adjusted_width, 10)  # حد أدنى 10
            adjusted_width = min(adjusted_width, 30)  # حد أقصى 30
            worksheet.set_column(col, col, adjusted_width)
    
        # إضافة المجموع الكلي
        if len(branches) > 1:
            col = 0
            worksheet.write(row, col, 'الإجمالي', header_format); col += 1
            
            worksheet.write(row, col, totals['cash_sales'], total_format); col += 1
            worksheet.write(row, col, totals['cash_payments'].get('نقدي', 0), total_format); col += 1
            worksheet.write(row, col, totals['cash_payments'].get('شبكة', 0), total_format); col += 1
            worksheet.write(row, col, totals['cash_payments'].get('حوالة', 0), total_format); col += 1
            
            worksheet.write(row, col, totals['credit_collection'], total_format); col += 1
            worksheet.write(row, col, totals['credit_payments'].get('نقدي', 0), total_format); col += 1
            worksheet.write(row, col, totals['credit_payments'].get('شبكة', 0), total_format); col += 1
            worksheet.write(row, col, totals['credit_payments'].get('حوالة', 0), total_format); col += 1
            
            worksheet.write(row, col, totals['cash_and_collection'], total_format); col += 1
            worksheet.write(row, col, totals['net_cash'], total_format); col += 1
            worksheet.write(row, col, totals['credit_refunds'], total_format); col += 1
            worksheet.write(row, col, totals['cash_refunds'], total_format); col += 1
            worksheet.write(row, col, totals['credit_sales'], total_format); col += 1
            worksheet.write(row, col, totals['total_sales'], total_format)
            
            row += 2
    
        # إضافة جدول طرق الدفع
        if totals['payment_methods']:
            # عنوان جدول طرق الدفع
            worksheet.merge_range(row, 0, row, 1, 'إجمالي الدفع حسب طريقة الدفع', merged_header_format)
            row += 1
            
            # عناوين الأعمدة
            worksheet.write(row, 0, 'طريقة الدفع', header_format)
            worksheet.write(row, 1, 'المبلغ', header_format)
            row += 1
            
            # بيانات طرق الدفع
            for method, amount in sorted(totals['payment_methods'].items()):
                worksheet.write(row, 0, method, text_format)
                worksheet.write(row, 1, amount, currency_format)
                row += 1
            
            # المجموع الكلي لطرق الدفع
            worksheet.write(row, 0, 'الإجمالي', header_format)
            worksheet.write(row, 1, sum(totals['payment_methods'].values()), total_format)
            row += 1
    
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

    def action_generate_pdf_report(self):
        """إجراء لإنشاء وتنزيل تقرير PDF"""
        self.ensure_one()
        try:
            report_data = self.generate_pdf_report()
            
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
            _logger.error("Failed to generate PDF report: %s", str(e))
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
