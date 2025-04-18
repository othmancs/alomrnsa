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
        
        # عنوان "إجمالي المبيعات النقدية" والمدفوعات
        worksheet.merge_range(row, 1, row, 1, 'إجمالي المبيعات النقدية', merged_header_format)
        
        # عناوين طرق الدفع للمبيعات النقدية
        payment_methods = self._get_payment_methods('inbound')
        num_payment_methods = len(payment_methods)
        if num_payment_methods > 0:
            worksheet.merge_range(row, 2, row, 1 + num_payment_methods, 
                                 'تقسيم المدفوعات للمبيعات النقدية', merged_header_format)
        
        # عنوان "إجمالي التحصيل الآجل"
        next_col = 2 + num_payment_methods
        worksheet.merge_range(row, next_col, row, next_col, 
                             'إجمالي التحصيل الآجل', merged_header_format)
        next_col += 1
        
        # عناوين طرق الدفع للتحصيل الآجل
        if num_payment_methods > 0:
            worksheet.merge_range(row, next_col, row, next_col + num_payment_methods - 1, 
                                 'تقسيم المدفوعات للتحصيل الآجل', merged_header_format)
            next_col += num_payment_methods
        
        # العناوين المتبقية
        titles = [
            'نقدي & التحصيل',
            'صافي الصندوق',
            'الارجاعات غير المستردة',
            'الارجاعات المستردة',
            'إجمالي المبيعات الآجلة',
            'إجمالي المبيعات'
        ]
        
        for idx, title in enumerate(titles):
            worksheet.write(row, next_col + idx, title, header_format)
    
        # الصف التالي (صف العناوين الفرعية لطرق الدفع)
        row += 1
        
        # كتابة أسماء طرق الدفع في الصف الثاني
        worksheet.write(row, 0, '', header_format)  # عمود الفرع فارغ
        worksheet.write(row, 1, '', header_format)  # تحت إجمالي المبيعات النقدية
        
        # كتابة أسماء طرق الدفع للمبيعات النقدية
        for idx, method in enumerate(payment_methods):
            worksheet.write(row, 2 + idx, method, header_format)
        
        # كتابة أسماء طرق الدفع للتحصيل الآجل
        next_col = 2 + num_payment_methods
        worksheet.write(row, next_col, '', header_format)  # تحت إجمالي التحصيل الآجل
        next_col += 1
        
        for idx, method in enumerate(payment_methods):
            worksheet.write(row, next_col + idx, method, header_format)
        
        # العناوين المتبقية تبقى فارغة في الصف الثاني
        remaining_cols = next_col + num_payment_methods
        for col in range(remaining_cols, remaining_cols + len(titles)):
            worksheet.write(row, col, '', header_format)
    
        # تحديد عرض الأعمدة
        worksheet.set_column(0, 0, 30)  # عمود الفرع
        worksheet.set_column(1, 20, 20)  # الأعمدة الرقمية
    
        # جمع البيانات لكل فرع على حدة
        branch_ids = self.branch_ids.ids if self.branch_ids else self.env['res.branch'].search([]).ids
        branches = self.env['res.branch'].browse(branch_ids)
    
        # متغيرات لتخزين الإجماليات
        totals = {
            'cash_sales': 0,
            'payment_methods_cash': {method: 0 for method in payment_methods},
            'credit_collection': 0,
            'payment_methods_credit': {method: 0 for method in payment_methods},
            'cash_and_collection': 0,
            'net_cash': 0,
            'non_refunded_returns': 0,
            'refunded_returns': 0,
            'credit_sales': 0,
            'total_sales': 0
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
            
            # حساب المدفوعات لكل طريقة دفع للمبيعات النقدية
            payment_methods_cash = {method: 0 for method in payment_methods}
            for invoice in cash_invoices:
                for payment in invoice._get_reconciled_payments():
                    if payment.payment_method_line_id:
                        method_name = payment.payment_method_line_id.name or 'غير محدد'
                        if method_name in payment_methods_cash:
                            payment_methods_cash[method_name] += payment.amount
    
            # 2. حساب التحصيل الآجل (مدفوعات لفواتير قديمة)
            credit_collection_domain = [
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
                ('payment_type', '=', 'inbound'),
                ('state', '=', 'posted'),
                ('is_internal_transfer', '=', False),
                ('company_id', '=', self.company_id.id),
                ('branch_id', '=', branch.id),
                ('invoice_ids.invoice_date', '<', self.date_from)  # فواتير من تاريخ سابق
            ]
            credit_payments = self.env['account.payment'].search(credit_collection_domain)
            branch_credit_collection = sum(payment.amount for payment in credit_payments)
            
            # حساب المدفوعات لكل طريقة دفع للتحصيل الآجل
            payment_methods_credit = {method: 0 for method in payment_methods}
            for payment in credit_payments:
                if payment.payment_method_line_id:
                    method_name = payment.payment_method_line_id.name or 'غير محدد'
                    if method_name in payment_methods_credit:
                        payment_methods_credit[method_name] += payment.amount
    
            # 3. حساب نقدي & التحصيل (المبيعات النقدية + التحصيل الآجل)
            branch_cash_and_collection = branch_cash_sales + branch_credit_collection
    
            # 4. حساب الارجاعات المستردة (مدفوعة)
            refunded_returns_domain = [
                ('invoice_date', '>=', self.date_from),
                ('invoice_date', '<=', self.date_to),
                ('move_type', '=', 'out_refund'),
                ('state', '=', 'posted'),
                ('payment_state', '=', 'paid'),
                ('company_id', '=', self.company_id.id),
                ('branch_id', '=', branch.id)
            ]
            refunded_returns = self.env['account.move'].search(refunded_returns_domain)
            branch_refunded_returns = sum(abs(refund.amount_untaxed) for refund in refunded_returns)
    
            # 5. حساب الارجاعات غير المستردة (غير مدفوعة)
            non_refunded_returns_domain = [
                ('invoice_date', '>=', self.date_from),
                ('invoice_date', '<=', self.date_to),
                ('move_type', '=', 'out_refund'),
                ('state', '=', 'posted'),
                ('payment_state', '=', 'not_paid'),
                ('company_id', '=', self.company_id.id),
                ('branch_id', '=', branch.id)
            ]
            non_refunded_returns = self.env['account.move'].search(non_refunded_returns_domain)
            branch_non_refunded_returns = sum(abs(refund.amount_untaxed) for refund in non_refunded_returns)
    
            # 6. حساب صافي الصندوق (نقدي & التحصيل - الارجاعات المستردة)
            branch_net_cash = branch_cash_and_collection - branch_refunded_returns
    
            # 7. حساب المبيعات الآجلة (فواتير بنفس تاريخ التقرير وغير مدفوعة)
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
    
            # 8. حساب إجمالي المبيعات (النقدية + الآجلة)
            branch_total_sales = branch_cash_sales + branch_credit_sales
    
            # تحديث الإجماليات
            totals['cash_sales'] += branch_cash_sales
            for method in payment_methods:
                totals['payment_methods_cash'][method] += payment_methods_cash.get(method, 0)
                totals['payment_methods_credit'][method] += payment_methods_credit.get(method, 0)
            totals['credit_collection'] += branch_credit_collection
            totals['cash_and_collection'] += branch_cash_and_collection
            totals['net_cash'] += branch_net_cash
            totals['non_refunded_returns'] += branch_non_refunded_returns
            totals['refunded_returns'] += branch_refunded_returns
            totals['credit_sales'] += branch_credit_sales
            totals['total_sales'] += branch_total_sales
    
            # كتابة بيانات الفرع
            col = 0
            worksheet.write(row, col, branch.name, text_format); col += 1
            
            # إجمالي المبيعات النقدية
            worksheet.write(row, col, branch_cash_sales, currency_format); col += 1
            
            # طرق الدفع للمبيعات النقدية
            for method in payment_methods:
                worksheet.write(row, col, payment_methods_cash.get(method, 0), currency_format)
                col += 1
            
            # إجمالي التحصيل الآجل
            worksheet.write(row, col, branch_credit_collection, currency_format); col += 1
            
            # طرق الدفع للتحصيل الآجل
            for method in payment_methods:
                worksheet.write(row, col, payment_methods_credit.get(method, 0), currency_format)
                col += 1
            
            # بقية الأعمدة
            worksheet.write(row, col, branch_cash_and_collection, currency_format); col += 1
            worksheet.write(row, col, branch_net_cash, currency_format); col += 1
            worksheet.write(row, col, branch_non_refunded_returns, currency_format); col += 1
            worksheet.write(row, col, branch_refunded_returns, currency_format); col += 1
            worksheet.write(row, col, branch_credit_sales, currency_format); col += 1
            worksheet.write(row, col, branch_total_sales, currency_format)
    
            row += 1
    
        # إضافة المجموع الكلي إذا كان هناك أكثر من فرع
        if len(branches) > 1:
            col = 0
            worksheet.write(row, col, 'الإجمالي', header_format); col += 1
            
            # إجمالي المبيعات النقدية
            worksheet.write(row, col, totals['cash_sales'], total_format); col += 1
            
            # طرق الدفع للمبيعات النقدية
            for method in payment_methods:
                worksheet.write(row, col, totals['payment_methods_cash'].get(method, 0), total_format)
                col += 1
            
            # إجمالي التحصيل الآجل
            worksheet.write(row, col, totals['credit_collection'], total_format); col += 1
            
            # طرق الدفع للتحصيل الآجل
            for method in payment_methods:
                worksheet.write(row, col, totals['payment_methods_credit'].get(method, 0), total_format)
                col += 1
            
            # بقية الأعمدة
            worksheet.write(row, col, totals['cash_and_collection'], total_format); col += 1
            worksheet.write(row, col, totals['net_cash'], total_format); col += 1
            worksheet.write(row, col, totals['non_refunded_returns'], total_format); col += 1
            worksheet.write(row, col, totals['refunded_returns'], total_format); col += 1
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

    def _get_payment_methods(self, payment_type):
        """الحصول على طرق الدفع المحددة في الشركة"""
        payment_methods = self.env['account.payment.method.line'].search([
            ('payment_type', '=', payment_type),
            ('company_id', '=', self.company_id.id)
        ])
        return [method.name for method in payment_methods]

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
