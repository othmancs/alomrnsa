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


class CustomerAccountStatement(models.Model):
    _name = 'customer.account.statement'
    _description = 'كشف حساب العميل'
    _rec_name = 'partner_id'
    _order = 'date_from desc'

    date_from = fields.Date(string='من تاريخ', default=fields.Date.today(), required=True)
    date_to = fields.Date(string='إلى تاريخ', default=fields.Date.today(), required=True)
    partner_id = fields.Many2one(
        'res.partner', string='العميل',
        domain=[('customer_rank', '>', 0)], required=True
    )
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
    initial_balance = fields.Monetary(
        string='الرصيد الافتتاحي',
        currency_field='company_currency_id',
        compute='_compute_balances', store=True
    )
    total_invoices = fields.Monetary(
        string='إجمالي الفواتير',
        currency_field='company_currency_id',
        compute='_compute_balances', store=True
    )
    total_credit_notes = fields.Monetary(
        string='إجمالي الإشعارات الدائنة',
        currency_field='company_currency_id',
        compute='_compute_balances', store=True
    )
    total_payments = fields.Monetary(
        string='إجمالي المقبوضات',
        currency_field='company_currency_id',
        compute='_compute_balances', store=True
    )
    total_debit = fields.Monetary(
        string='إجمالي المدين',
        currency_field='company_currency_id',
        compute='_compute_balances', store=True
    )
    total_credit = fields.Monetary(
        string='إجمالي الدائن',
        currency_field='company_currency_id',
        compute='_compute_balances', store=True
    )
    final_balance = fields.Monetary(
        string='الرصيد الختامي',
        currency_field='company_currency_id',
        compute='_compute_balances', store=True
    )
    transaction_lines = fields.Html(
        string='حركات الحساب',
        compute='_compute_transaction_lines',
        sanitize=False
    )

    @api.depends('date_from', 'date_to', 'partner_id', 'company_id', 'branch_ids')
    def _compute_balances(self):
        for record in self:
            # حساب الرصيد الافتتاحي (جميع الحركات قبل تاريخ البدء)
            initial_domain = [
                ('date', '<', record.date_from),
                ('partner_id', '=', record.partner_id.id),
                ('company_id', '=', record.company_id.id),
                ('move_id.state', '=', 'posted')
            ]
            if record.branch_ids:
                initial_domain.append(('branch_id', 'in', record.branch_ids.ids))

            initial_lines = self.env['account.move.line'].search(initial_domain)
            record.initial_balance = sum(line.balance for line in initial_lines)

            # حساب الحركات خلال الفترة
            record.total_invoices = 0.0
            record.total_credit_notes = 0.0
            record.total_payments = 0.0
            
            # الحصول على جميع الفواتير والاشعارات الدائنة والمقبوضات
            moves = self._get_account_moves()
            
            for move in moves:
                if move.move_type in ('out_invoice', 'out_refund', 'out_receipt'):
                    amount = move.amount_total_signed
                    if move.move_type == 'out_invoice':
                        record.total_invoices += amount
                    elif move.move_type == 'out_refund':
                        record.total_credit_notes += amount
                    elif move.move_type == 'out_receipt':
                        record.total_payments += amount
            
            # حساب إجمالي المدين والدائن
            record.total_debit = record.total_invoices
            record.total_credit = abs(record.total_credit_notes) + abs(record.total_payments)
            
            # حساب الرصيد الختامي
            record.final_balance = record.initial_balance + record.total_debit - record.total_credit

    def _get_account_moves(self):
        """الحصول على حركات الحساب (فواتير، اشعارات دائنة، مقبوضات)"""
        self.ensure_one()
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('partner_id', '=', self.partner_id.id),
            ('company_id', '=', self.company_id.id),
            ('state', '=', 'posted'),
            ('move_type', 'in', ('out_invoice', 'out_refund', 'out_receipt'))
        ]
        if self.branch_ids:
            domain.append(('branch_id', 'in', self.branch_ids.ids))
        
        return self.env['account.move'].search(domain, order='date, id')

    @api.depends('date_from', 'date_to', 'partner_id', 'company_id', 'branch_ids')
    def _compute_transaction_lines(self):
        for record in self:
            # إنشاء جدول HTML لعرض الحركات
            html_lines = []
            html_lines.append("""
                <style>
                    .total-row {
                        background-color: #f2f2f2;
                        font-weight: bold;
                    }
                    .invoice-row {
                        background-color: #e6f7ff;
                    }
                    .credit-note-row {
                        background-color: #fff2e6;
                    }
                    .payment-row {
                        background-color: #e6ffe6;
                    }
                </style>
                <table class="table table-bordered" style="width:100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background-color: #4472C4; color: white;">
                            <th style="padding: 8px; border: 1px solid #ddd;">التاريخ</th>
                            <th style="padding: 8px; border: 1px solid #ddd;">الرقم</th>
                            <th style="padding: 8px; border: 1px solid #ddd;">البيان</th>
                            <th style="padding: 8px; border: 1px solid #ddd;">الفرع</th>
                            <th style="padding: 8px; border: 1px solid #ddd;">النوع</th>
                            <th style="padding: 8px; border: 1px solid #ddd;">مدين</th>
                            <th style="padding: 8px; border: 1px solid #ddd;">دائن</th>
                            <th style="padding: 8px; border: 1px solid #ddd;">الرصيد</th>
                        </tr>
                    </thead>
                    <tbody>
            """)

            # إضافة الرصيد الافتتاحي
            html_lines.append(f"""
                <tr style="background-color: #f2f2f2;">
                    <td style="padding: 8px; border: 1px solid #ddd;">{record.date_from}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;"></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">رصيد افتتاحي</td>
                    <td style="padding: 8px; border: 1px solid #ddd;"></td>
                    <td style="padding: 8px; border: 1px solid #ddd;"></td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right;"></td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right;"></td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">{format(record.initial_balance, '.2f')}</td>
                </tr>
            """)

            running_balance = record.initial_balance
            
            # الحصول على حركات الحساب
            moves = record._get_account_moves()
            
            # إضافة الحركات
            for move in moves:
                move_type = ''
                amount = move.amount_total_signed
                debit = 0.0
                credit = 0.0
                
                if move.move_type == 'out_invoice':
                    move_type = 'فاتورة بيع'
                    debit = amount
                    running_balance += debit
                    row_class = 'invoice-row'
                elif move.move_type == 'out_refund':
                    move_type = 'اشعار دائن'
                    credit = abs(amount)
                    running_balance -= credit
                    row_class = 'credit-note-row'
                elif move.move_type == 'out_receipt':
                    move_type = 'مقبوضات'
                    credit = abs(amount)
                    running_balance -= credit
                    row_class = 'payment-row'
                
                html_lines.append(f"""
                    <tr class="{row_class}">
                        <td style="padding: 8px; border: 1px solid #ddd;">{move.date}</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{move.name or ''}</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{move.invoice_origin or move.ref or ''}</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{move.branch_id.name or ''}</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{move_type}</td>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">{format(debit, '.2f') if debit > 0 else ''}</td>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">{format(credit, '.2f') if credit > 0 else ''}</td>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">{format(running_balance, '.2f')}</td>
                    </tr>
                """)
            
            # إضافة الإجماليات
            html_lines.append(f"""
                <tr class="total-row">
                    <td colspan="5" style="padding: 8px; border: 1px solid #ddd; text-align: right;">إجمالي الفواتير</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">{format(record.total_invoices, '.2f')}</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right;"></td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right;"></td>
                </tr>
                <tr class="total-row">
                    <td colspan="5" style="padding: 8px; border: 1px solid #ddd; text-align: right;">إجمالي الإشعارات الدائنة</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right;"></td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">{format(abs(record.total_credit_notes), '.2f')}</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right;"></td>
                </tr>
                <tr class="total-row">
                    <td colspan="5" style="padding: 8px; border: 1px solid #ddd; text-align: right;">إجمالي المقبوضات</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right;"></td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">{format(abs(record.total_payments), '.2f')}</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right;"></td>
                </tr>
                <tr class="total-row">
                    <td colspan="5" style="padding: 8px; border: 1px solid #ddd; text-align: right;">إجمالي المدين</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">{format(record.total_debit, '.2f')}</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right;"></td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right;"></td>
                </tr>
                <tr class="total-row">
                    <td colspan="5" style="padding: 8px; border: 1px solid #ddd; text-align: right;">إجمالي الدائن</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right;"></td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">{format(record.total_credit, '.2f')}</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right;"></td>
                </tr>
                <tr class="total-row">
                    <td colspan="5" style="padding: 8px; border: 1px solid #ddd; text-align: right;">الرصيد الختامي</td>
                    <td colspan="2" style="padding: 8px; border: 1px solid #ddd; text-align: center;">{format(record.final_balance, '.2f')}</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right;"></td>
                </tr>
            """)

            html_lines.append("""
                    </tbody>
                </table>
            """)

            record.transaction_lines = '\n'.join(html_lines)

    @api.onchange('date_from')
    def _onchange_date_from(self):
        if self.date_from and not self.date_to:
            self.date_to = self.date_from

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_from and record.date_to and record.date_from > record.date_to:
                raise models.ValidationError("تاريخ البداية يجب أن يكون قبل تاريخ النهاية")

    def action_view_transactions(self):
        self.ensure_one()
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('partner_id', '=', self.partner_id.id),
            ('company_id', '=', self.company_id.id),
            ('state', '=', 'posted'),
            ('move_type', 'in', ('out_invoice', 'out_refund', 'out_receipt'))
        ]
        if self.branch_ids:
            domain.append(('branch_id', 'in', self.branch_ids.ids))
        action['domain'] = domain
        action['context'] = {
            'search_default_partner_id': self.partner_id.id,
            'create': False
        }
        return action

    def generate_account_statement_report(self):
        """إنشاء تقرير Excel لكشف حساب العميل"""
        self.ensure_one()
        # إنشاء كتاب Excel
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True, 'right_to_left': False})
        worksheet = workbook.add_worksheet('كشف حساب العميل')
    
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
        label_format = workbook.add_format({
            'bold': True, 'align': 'right', 'border': 1
        })
        invoice_format = workbook.add_format({
            'border': 1, 'align': 'right', 'bg_color': '#E6F7FF'
        })
        credit_note_format = workbook.add_format({
            'border': 1, 'align': 'right', 'bg_color': '#FFF2E6'
        })
        payment_format = workbook.add_format({
            'border': 1, 'align': 'right', 'bg_color': '#E6FFE6'
        })
    
        # إضافة شعار الشركة
        row = 0
        if self.company_id.logo:
            try:
                image_data = io.BytesIO(base64.b64decode(self.company_id.logo))
                worksheet.merge_range(row, 5, row+1, 5, '')
                worksheet.insert_image(row, 5, 'logo.png', {
                    'image_data': image_data,
                    'x_scale': 0.15, 
                    'y_scale': 0.15,
                    'x_offset': 10, 
                    'y_offset': 10,
                    'object_position': 3,
                    'positioning': 1
                })
                worksheet.set_row(row, 80)
                row += 1
                worksheet.set_row(row, 15)
                row += 1
            except Exception as e:
                _logger.error(f"Failed to insert company logo: {str(e)}")
                pass
    
        # إضافة عنوان التقرير
        worksheet.merge_range(row, 0, row, 7, 'كشف حساب العميل', title_format)
        row += 1
        worksheet.merge_range(row, 0, row, 7, f'العميل: {self.partner_id.name}', 
                             workbook.add_format({'align': 'center', 'font_size': 12}))
        row += 1
        worksheet.merge_range(row, 0, row, 7, f'من {self.date_from} إلى {self.date_to}', 
                             workbook.add_format({'align': 'center', 'font_size': 12}))
        row += 2
    
        # إضافة ملخص الرصيد
        worksheet.write(row, 0, 'الرصيد الافتتاحي', label_format)
        worksheet.write(row, 1, round(self.initial_balance, 2), currency_format)
        row += 1
        
        worksheet.write(row, 0, 'إجمالي الفواتير', label_format)
        worksheet.write(row, 1, round(self.total_invoices, 2), currency_format)
        row += 1
        
        worksheet.write(row, 0, 'إجمالي الإشعارات الدائنة', label_format)
        worksheet.write(row, 1, round(abs(self.total_credit_notes), 2), currency_format)
        row += 1
        
        worksheet.write(row, 0, 'إجمالي المقبوضات', label_format)
        worksheet.write(row, 1, round(abs(self.total_payments), 2), currency_format)
        row += 1
        
        worksheet.write(row, 0, 'إجمالي المدين', label_format)
        worksheet.write(row, 1, round(self.total_debit, 2), currency_format)
        row += 1
        
        worksheet.write(row, 0, 'إجمالي الدائن', label_format)
        worksheet.write(row, 1, round(self.total_credit, 2), currency_format)
        row += 1
        
        worksheet.write(row, 0, 'الرصيد الختامي', label_format)
        worksheet.write(row, 1, round(self.final_balance, 2), total_format)
        row += 2
    
        # إنشاء صف العناوين
        headers = [
            'التاريخ',
            'الرقم',
            'البيان',
            'الفرع',
            'النوع',
            'مدين',
            'دائن',
            'الرصيد'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(row, col, header, header_format)
        row += 1
    
        # إضافة الرصيد الافتتاحي
        worksheet.write(row, 0, self.date_from.strftime('%Y-%m-%d'), text_format)
        worksheet.write(row, 1, '', text_format)
        worksheet.write(row, 2, 'رصيد افتتاحي', text_format)
        worksheet.write(row, 3, '', text_format)
        worksheet.write(row, 4, '', text_format)
        worksheet.write(row, 5, '', currency_format)
        worksheet.write(row, 6, '', currency_format)
        worksheet.write(row, 7, round(self.initial_balance, 2), currency_format)
        row += 1
    
        running_balance = self.initial_balance
        
        # الحصول على حركات الحساب
        moves = self._get_account_moves()
        
        # إضافة الحركات
        for move in moves:
            move_type = ''
            amount = move.amount_total_signed
            debit = 0.0
            credit = 0.0
            cell_format = text_format
            
            if move.move_type == 'out_invoice':
                move_type = 'فاتورة بيع'
                debit = amount
                running_balance += debit
                cell_format = invoice_format
            elif move.move_type == 'out_refund':
                move_type = 'اشعار دائن'
                credit = abs(amount)
                running_balance -= credit
                cell_format = credit_note_format
            elif move.move_type == 'out_receipt':
                move_type = 'مقبوضات'
                credit = abs(amount)
                running_balance -= credit
                cell_format = payment_format
            
            worksheet.write(row, 0, move.date.strftime('%Y-%m-%d'), cell_format)
            worksheet.write(row, 1, move.name or '', cell_format)
            worksheet.write(row, 2, move.invoice_origin or move.ref or '', cell_format)
            worksheet.write(row, 3, move.branch_id.name or '', cell_format)
            worksheet.write(row, 4, move_type, cell_format)
            worksheet.write(row, 5, round(debit, 2) if debit > 0 else '', currency_format)
            worksheet.write(row, 6, round(credit, 2) if credit > 0 else '', currency_format)
            worksheet.write(row, 7, round(running_balance, 2), currency_format)
            row += 1
        
        # إضافة الإجماليات
        worksheet.write(row, 0, 'إجمالي الفواتير', label_format)
        worksheet.write(row, 1, '', label_format)
        worksheet.write(row, 2, '', label_format)
        worksheet.write(row, 3, '', label_format)
        worksheet.write(row, 4, '', label_format)
        worksheet.write(row, 5, round(self.total_invoices, 2), total_format)
        worksheet.write(row, 6, '', label_format)
        worksheet.write(row, 7, '', label_format)
        row += 1
        
        worksheet.write(row, 0, 'إجمالي الإشعارات الدائنة', label_format)
        worksheet.write(row, 1, '', label_format)
        worksheet.write(row, 2, '', label_format)
        worksheet.write(row, 3, '', label_format)
        worksheet.write(row, 4, '', label_format)
        worksheet.write(row, 5, '', label_format)
        worksheet.write(row, 6, round(abs(self.total_credit_notes), 2), total_format)
        worksheet.write(row, 7, '', label_format)
        row += 1
        
        worksheet.write(row, 0, 'إجمالي المقبوضات', label_format)
        worksheet.write(row, 1, '', label_format)
        worksheet.write(row, 2, '', label_format)
        worksheet.write(row, 3, '', label_format)
        worksheet.write(row, 4, '', label_format)
        worksheet.write(row, 5, '', label_format)
        worksheet.write(row, 6, round(abs(self.total_payments), 2), total_format)
        worksheet.write(row, 7, '', label_format)
        row += 1
        
        worksheet.write(row, 0, 'إجمالي المدين', label_format)
        worksheet.write(row, 1, '', label_format)
        worksheet.write(row, 2, '', label_format)
        worksheet.write(row, 3, '', label_format)
        worksheet.write(row, 4, '', label_format)
        worksheet.write(row, 5, round(self.total_debit, 2), total_format)
        worksheet.write(row, 6, '', label_format)
        worksheet.write(row, 7, '', label_format)
        row += 1
        
        worksheet.write(row, 0, 'إجمالي الدائن', label_format)
        worksheet.write(row, 1, '', label_format)
        worksheet.write(row, 2, '', label_format)
        worksheet.write(row, 3, '', label_format)
        worksheet.write(row, 4, '', label_format)
        worksheet.write(row, 5, '', label_format)
        worksheet.write(row, 6, round(self.total_credit, 2), total_format)
        worksheet.write(row, 7, '', label_format)
        row += 1
        
        worksheet.write(row, 0, 'الرصيد الختامي', label_format)
        worksheet.write(row, 1, '', label_format)
        worksheet.write(row, 2, '', label_format)
        worksheet.write(row, 3, '', label_format)
        worksheet.write(row, 4, '', label_format)
        worksheet.merge_range(row, 5, row, 6, round(self.final_balance, 2), total_format)
        worksheet.write(row, 7, '', label_format)
        row += 1
    
        # ضبط عرض الأعمدة
        worksheet.set_column(0, 0, 12)  # التاريخ
        worksheet.set_column(1, 1, 15)  # الرقم
        worksheet.set_column(2, 2, 30)  # البيان
        worksheet.set_column(3, 3, 15)  # الفرع
        worksheet.set_column(4, 4, 15)  # النوع
        worksheet.set_column(5, 7, 15)  # الأرقام
    
        # إغلاق الكتاب وحفظه
        workbook.close()
        output.seek(0)
    
        return {
            'file_name': f"كشف_حساب_{self.partner_id.name}_{self.date_from}_إلى_{self.date_to}.xlsx",
            'file_content': output.read(),
            'file_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }

    def action_generate_excel_report(self):
        """إجراء لإنشاء وتنزيل التقرير"""
        self.ensure_one()
        try:
            report_data = self.generate_account_statement_report()
            
            attachment = self.env['ir.attachment'].create({
                'name': report_data['file_name'],
                'datas': base64.b64encode(report_data['file_content']),
                'res_model': 'customer.account.statement',
                'res_id': self.id,
                'type': 'binary'
            })
            
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s?download=true' % attachment.id,
                'target': 'self',
            }
        except Exception as e:
            _logger.error("Failed to generate account statement report: %s", str(e))
            raise

    def generate_pdf_report(self):
        """إنشاء تقرير PDF لكشف حساب العميل"""
        self.ensure_one()
        try:
            # إنشاء مستند PDF
            output = io.BytesIO()
            doc = SimpleDocTemplate(output, pagesize=landscape(letter), rightMargin=20, leftMargin=20, topMargin=30, bottomMargin=30)
            
            # تسجيل خط عربي إذا لزم الأمر
            try:
                pdfmetrics.registerFont(TTFont('Arabic', 'arial.ttf'))
            except:
                _logger.warning("Failed to register Arabic font, using default")
            
            # أنماط النص
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Title'],
                fontName='Arabic',
                fontSize=16,
                alignment=1,  # 1=center
                textColor=colors.HexColor('#4472C4')
            )
            
            header_style = ParagraphStyle(
                'Header',
                parent=styles['Normal'],
                fontName='Arabic',
                fontSize=12,
                alignment=1,  # 1=center
                textColor=colors.white,
                backColor=colors.HexColor('#4472C4')
            )
            
            normal_style = ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontName='Arabic',
                fontSize=10,
                alignment=2  # 2=right
            )
            
            currency_style = ParagraphStyle(
                'Currency',
                parent=styles['Normal'],
                fontName='Arabic',
                fontSize=10,
                alignment=2  # 2=right
            )
            
            total_style = ParagraphStyle(
                'Total',
                parent=styles['Normal'],
                fontName='Arabic',
                fontSize=10,
                alignment=2,  # 2=right
                fontWeight='bold',
                backColor=colors.HexColor('#D9E1F2')
            )
            
            # عناصر التقرير
            elements = []
            
            # إضافة عنوان التقرير
            title = Paragraph("كشف حساب العميل", title_style)
            elements.append(title)
            
            # إضافة معلومات العميل
            customer_info = Paragraph(f"العميل: {self.partner_id.name}", normal_style)
            elements.append(customer_info)
            
            # إضافة الفترة الزمنية
            date_range = Paragraph(f"من {self.date_from} إلى {self.date_to}", normal_style)
            elements.append(date_range)
            
            elements.append(Spacer(1, 20))
            
            # إضافة ملخص الرصيد
            balance_data = [
                ['الرصيد الافتتاحي', format(round(self.initial_balance, 2), ',.2f')],
                ['إجمالي الفواتير', format(round(self.total_invoices, 2), ',.2f')],
                ['إجمالي الإشعارات الدائنة', format(round(abs(self.total_credit_notes), 2), ',.2f')],
                ['إجمالي المقبوضات', format(round(abs(self.total_payments), 2), ',.2f')],
                ['إجمالي المدين', format(round(self.total_debit, 2), ',.2f')],
                ['إجمالي الدائن', format(round(self.total_credit, 2), ',.2f')],
                ['الرصيد الختامي', format(round(self.final_balance, 2), ',.2f')]
            ]
            
            balance_table = Table(balance_data, colWidths=[200, 100])
            balance_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f2f2f2')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(balance_table)
            elements.append(Spacer(1, 20))
            
            # إضافة حركات الحساب
            transaction_header = [
                'التاريخ',
                'الرقم',
                'البيان',
                'الفرع',
                'النوع',
                'مدين',
                'دائن',
                'الرصيد'
            ]
            
            transaction_data = [transaction_header]
            
            # إضافة الرصيد الافتتاحي
            transaction_data.append([
                self.date_from.strftime('%Y-%m-%d'),
                '',
                'رصيد افتتاحي',
                '',
                '',
                '',
                '',
                format(round(self.initial_balance, 2), ',.2f')
            ])
            
            running_balance = self.initial_balance
            
            # الحصول على حركات الحساب
            moves = self._get_account_moves()
            
            # إضافة الحركات
            for move in moves:
                move_type = ''
                amount = move.amount_total_signed
                debit = 0.0
                credit = 0.0
                
                if move.move_type == 'out_invoice':
                    move_type = 'فاتورة بيع'
                    debit = amount
                    running_balance += debit
                elif move.move_type == 'out_refund':
                    move_type = 'اشعار دائن'
                    credit = abs(amount)
                    running_balance -= credit
                elif move.move_type == 'out_receipt':
                    move_type = 'مقبوضات'
                    credit = abs(amount)
                    running_balance -= credit
                
                transaction_data.append([
                    move.date.strftime('%Y-%m-%d'),
                    move.name or '',
                    move.invoice_origin or move.ref or '',
                    move.branch_id.name or '',
                    move_type,
                    format(round(debit, 2), ',.2f') if debit > 0 else '',
                    format(round(credit, 2), ',.2f') if credit > 0 else '',
                    format(round(running_balance, 2), ',.2f')
                ])
            
            # إضافة الإجماليات
            transaction_data.append([
                'إجمالي الفواتير', '', '', '', '',
                format(round(self.total_invoices, 2), ',.2f'), '', ''
            ])
            transaction_data.append([
                'إجمالي الإشعارات الدائنة', '', '', '', '', '',
                format(round(abs(self.total_credit_notes), 2), ',.2f'), ''
            ])
            transaction_data.append([
                'إجمالي المقبوضات', '', '', '', '', '',
                format(round(abs(self.total_payments), 2), ',.2f'), ''
            ])
            transaction_data.append([
                'إجمالي المدين', '', '', '', '',
                format(round(self.total_debit, 2), ',.2f'), '', ''
            ])
            transaction_data.append([
                'إجمالي الدائن', '', '', '', '', '',
                format(round(self.total_credit, 2), ',.2f'), ''
            ])
            transaction_data.append([
                'الرصيد الختامي', '', '', '', '', '', '',
                format(round(self.final_balance, 2), ',.2f')
            ])
            
            # إنشاء جدول الحركات
            transaction_table = Table(transaction_data, colWidths=[60, 60, 120, 60, 60, 60, 60, 60])
            transaction_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
                ('TOPPADDING', (0, 0), (-1, 0), 5),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, -7), (-1, -1), colors.HexColor('#f2f2f2')),
                ('FONTWEIGHT', (0, -7), (-1, -1), 'BOLD')
            ]))
            
            elements.append(transaction_table)
            
            # بناء مستند PDF
            doc.build(elements)
            output.seek(0)
            
            return {
                'file_name': f"كشف_حساب_{self.partner_id.name}_{self.date_from}_إلى_{self.date_to}.pdf",
                'file_content': output.read(),
                'file_type': 'application/pdf'
            }
        except Exception as e:
            _logger.error("Failed to generate PDF report: %s", str(e))
            raise

    def action_generate_pdf_report(self):
        """إجراء لإنشاء وتنزيل تقرير PDF"""
        self.ensure_one()
        try:
            report_data = self.generate_pdf_report()
            
            attachment = self.env['ir.attachment'].create({
                'name': report_data['file_name'],
                'datas': base64.b64encode(report_data['file_content']),
                'res_model': 'customer.account.statement',
                'res_id': self.id,
                'type': 'binary'
            })
            
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s?download=true' % attachment.id,
                'target': 'self',
            }
        except Exception as e:
            _logger.error("Failed to generate PDF report: %s", str(e))
            raise
