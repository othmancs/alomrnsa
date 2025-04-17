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
        subtitle_format = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter', 'font_size': 14
        })
        date_format = workbook.add_format({
            'align': 'center', 'valign': 'vcenter', 'font_size': 12
        })
        header_format = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'bg_color': '#93E262', 'font_color': 'black', 'border': 1, 
            'font_size': 12, 'text_wrap': True
        })
        merged_header_format = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'bg_color': '#E2EFDA', 'font_color': 'black', 'border': 1,
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
    
        # إضافة شعار الشركة إذا كان موجوداً في منتصف الصفحة
        row = 0
        if self.company_id.logo:
            try:
                logo_data = base64.b64decode(self.company_id.logo)
                
                col_logo = 5  # من العمود C
                    worksheet.merge_range(row, 0, row, 10, '') 
                    worksheet.insert_image(row, col_logo, 'company_logo.png', {
                    'image_data': io.BytesIO(logo_data),
                    'x_scale': 0.15,
                    'y_scale': 0.15,
                    'x_offset': 5,
                    'y_offset': 5,
                    'object_position': 1
                })
        
                worksheet.set_row(row, 60)  # اجعل الصف مرتفعاً لتتناسب الصورة
                row += 1  # انتقل إلى الصف التالي لكتابة النص تحته مباشرة
            except Exception as e:
                _logger.error("Failed to insert company logo: %s", str(e))
                row += 1
        
        # النص سيكون في الصف التالي
        company_name_row = row
        worksheet.merge_range(company_name_row, 0, company_name_row, 10, 
                              self.company_id.name, title_format)
        row += 1
        worksheet.merge_range('A3:J3', f'من {self.date_from} إلى {self.date_to}', date_format)
        worksheet.write(3, 0, '', workbook.add_format())
    
        # إنشاء صف العناوين المدمجة
        row = 4  # الصف الذي سيبدأ منه العناوين
        
        # عمود الفرع
        worksheet.write(row, 0, 'الفرع', header_format)
        
        # عنوان "تقرير المبيعات" المدمج فوق 5 أعمدة
        worksheet.merge_range(row, 1, row, 5, 'تقرير المبيعات', merged_header_format)
        
        # عنوان "تقرير التحصيل" المدمج فوق 5 أعمدة
        worksheet.merge_range(row, 6, row, 10, 'تقرير التحصيل', merged_header_format)
        
        # الصف التالي (صف العناوين الفرعية)
        row += 1
        
        # عناوين الأعمدة الفرعية تحت "تقرير المبيعات"
        worksheet.write(row, 1, 'مبيعات نقدية', header_format)
        worksheet.write(row, 2, 'مبيعات آجلة', header_format)
        worksheet.write(row, 3, 'إجمالي إرجاعات', header_format)
        worksheet.write(row, 4, 'صافي المبيعات', header_format)
        worksheet.write(row, 5, 'صافي المبيعات شامل الضريبة', header_format)
        
        # عناوين الأعمدة الفرعية تحت "تقرير التحصيل"
        worksheet.write(row, 6, 'تحصيل شبكة', header_format)
        worksheet.write(row, 7, 'تحصيل حوالات', header_format)
        worksheet.write(row, 8, 'تحصيل نقدي', header_format)
        worksheet.write(row, 9, 'إرجاعات مسددة نقدا', header_format)
        worksheet.write(row, 10, 'صافي التحصيل', header_format)
    
        # تحديد عرض الأعمدة
        worksheet.set_column(0, 0, 30)  # عمود الفرع
        worksheet.set_column(1, 10, 20)  # الأعمدة الرقمية
    
        # جمع البيانات لكل فرع على حدة
        branch_ids = self.branch_ids.ids if self.branch_ids else self.env['res.branch'].search([]).ids
        branches = self.env['res.branch'].browse(branch_ids)
    
        # متغيرات لتخزين الإجماليات
        totals = {
            'cash_sales': 0,
            'credit_sales': 0,
            'total_refunds': 0,
            'net_sales': 0,
            'net_sales_with_tax': 0,
            'network_collection': 0,
            'transfer_collection': 0,
            'cash_collection': 0,
            'cash_refunds': 0,
            'net_collection': 0
        }
    
        row += 1  # بدء البيانات من الصف التالي بعد العناوين
        for branch in branches:
            # 1. حساب المبيعات النقدية (فواتير بنفس تاريخ التقرير و محصلة أيضا في نفس تاريخها)
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
    
            # 2. حساب المبيعات الآجلة (فواتير بنفس تاريخ التقرير و غير محصلة أو محصلة في تاريخ لاحق)
            credit_sales_domain = [
                ('invoice_date', '>=', self.date_from),
                ('invoice_date', '<=', self.date_to),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', 'in', ['not_paid', 'partial']),
                ('company_id', '=', self.company_id.id),
                ('branch_id', '=', branch.id)
            ]
            credit_invoices = self.env['account.move'].search(credit_sales_domain)
            branch_credit_sales = sum(invoice.amount_untaxed for invoice in credit_invoices)
    
            # 3. حساب إجمالي الإرجاعات (كل الإرجاعات التي تمت في نفس تاريخ التقرير سواء مسددة أو غير مسددة)
            refunds_domain = [
                ('invoice_date', '>=', self.date_from),
                ('invoice_date', '<=', self.date_to),
                ('move_type', '=', 'out_refund'),
                ('state', '=', 'posted'),
                ('company_id', '=', self.company_id.id),
                ('branch_id', '=', branch.id)
            ]
            refunds = self.env['account.move'].search(refunds_domain)
            branch_total_refunds = sum(abs(refund.amount_untaxed) for refund in refunds)
    
            # 4. حساب صافي المبيعات (العمود 1 + العمود 2 - العمود 3)
            branch_net_sales = branch_cash_sales + branch_credit_sales - branch_total_refunds
    
            # 5. حساب صافي المبيعات شامل الضريبة (العمود 4 × 1.15)
            branch_net_sales_with_tax = branch_net_sales * 1.15
    
            # 6. تحصيل شبكة (عمليات التحصيل بالشبكة في نفس تاريخ التقرير)
            network_payments = self.env['account.payment'].search([
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
                ('payment_type', '=', 'inbound'),
                ('state', '=', 'posted'),
                ('payment_method_line_id.name', 'ilike', 'شبكة'),
                ('company_id', '=', self.company_id.id),
                ('branch_id', '=', branch.id)
            ])
            branch_network_collection = sum(payment.amount for payment in network_payments)
    
            # 7. تحصيل حوالات (عمليات التحصيل بحوالة أو شيك في نفس تاريخ التقرير)
            transfer_payments = self.env['account.payment'].search([
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
                ('payment_type', '=', 'inbound'),
                ('state', '=', 'posted'),
                ('payment_method_line_id.name', 'ilike', 'حوالة'),
                ('company_id', '=', self.company_id.id),
                ('branch_id', '=', branch.id)
            ])
            branch_transfer_collection = sum(payment.amount for payment in transfer_payments)
    
            # 8. تحصيل نقدي (عمليات التحصيل بالنقد في نفس تاريخ التقرير)
            cash_payments = self.env['account.payment'].search([
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
                ('payment_type', '=', 'inbound'),
                ('state', '=', 'posted'),
                ('payment_method_line_id.name', 'ilike', 'نقدي'),
                ('company_id', '=', self.company_id.id),
                ('branch_id', '=', branch.id)
            ])
            branch_cash_collection = sum(payment.amount for payment in cash_payments)
    
            # 9. إرجاعات مسددة نقدا (تأخذ نفس قيمة cash_refunds)
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
    
            # 10. صافي التحصيل (6 + 7 + 8 - 9)
            branch_net_collection = (branch_network_collection + 
                                   branch_transfer_collection + 
                                   branch_cash_collection - 
                                   branch_cash_refunds)
    
            # تحديث الإجماليات
            totals['cash_sales'] += branch_cash_sales
            totals['credit_sales'] += branch_credit_sales
            totals['total_refunds'] += branch_total_refunds
            totals['net_sales'] += branch_net_sales
            totals['net_sales_with_tax'] += branch_net_sales_with_tax
            totals['network_collection'] += branch_network_collection
            totals['transfer_collection'] += branch_transfer_collection
            totals['cash_collection'] += branch_cash_collection
            totals['cash_refunds'] += branch_cash_refunds
            totals['net_collection'] += branch_net_collection
    
            # كتابة بيانات الفرع
            col = 0
            worksheet.write(row, col, branch.name, text_format); col += 1
            worksheet.write(row, col, branch_cash_sales, currency_format); col += 1
            worksheet.write(row, col, branch_credit_sales, currency_format); col += 1
            worksheet.write(row, col, branch_total_refunds, currency_format); col += 1
            worksheet.write(row, col, branch_net_sales, currency_format); col += 1
            worksheet.write(row, col, branch_net_sales_with_tax, currency_format); col += 1
            worksheet.write(row, col, branch_network_collection, currency_format); col += 1
            worksheet.write(row, col, branch_transfer_collection, currency_format); col += 1
            worksheet.write(row, col, branch_cash_collection, currency_format); col += 1
            worksheet.write(row, col, branch_cash_refunds, currency_format); col += 1
            worksheet.write(row, col, branch_net_collection, currency_format)
    
            row += 1
    
        # إضافة المجموع الكلي إذا كان هناك أكثر من فرع
        if row > 6:  # تم تغيير الشرط لأننا بدأنا من صف أعلى
            col = 0
            worksheet.write(row, col, 'الإجمالي', header_format); col += 1
            worksheet.write(row, col, totals['cash_sales'], total_format); col += 1
            worksheet.write(row, col, totals['credit_sales'], total_format); col += 1
            worksheet.write(row, col, totals['total_refunds'], total_format); col += 1
            worksheet.write(row, col, totals['net_sales'], total_format); col += 1
            worksheet.write(row, col, totals['net_sales_with_tax'], total_format); col += 1
            worksheet.write(row, col, totals['network_collection'], total_format); col += 1
            worksheet.write(row, col, totals['transfer_collection'], total_format); col += 1
            worksheet.write(row, col, totals['cash_collection'], total_format); col += 1
            worksheet.write(row, col, totals['cash_refunds'], total_format); col += 1
            worksheet.write(row, col, totals['net_collection'], total_format)
    
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
