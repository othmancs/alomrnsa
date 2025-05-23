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

logger = logging.getLogger(__name__)

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

    # الحقول المحسوبة (تمت إزالة store=True)
    initial_balance = fields.Monetary(
        string='الرصيد الافتتاحي',
        currency_field='company_currency_id',
        compute='_compute_balances'
    )
    total_invoices = fields.Monetary(
        string='إجمالي الفواتير',
        currency_field='company_currency_id',
        compute='_compute_balances'
    )
    total_refunds = fields.Monetary(
        string='إجمالي الإشعارات الدائنة',
        currency_field='company_currency_id',
        compute='_compute_balances'
    )
    total_payments = fields.Monetary(
        string='إجمالي المقبوضات',
        currency_field='company_currency_id',
        compute='_compute_balances'
    )
    total_debit = fields.Monetary(
        string='إجمالي المدين',
        currency_field='company_currency_id',
        compute='_compute_balances'
    )
    total_credit = fields.Monetary(
        string='إجمالي الدائن',
        currency_field='company_currency_id',
        compute='_compute_balances'
    )
    final_balance = fields.Monetary(
        string='الرصيد الختامي',
        currency_field='company_currency_id',
        compute='_compute_balances'
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
                ('move_id.state', '=', 'posted'),
                ('account_id.account_type', '=', 'asset_receivable')
            ]
            if record.branch_ids:
                initial_domain.append(('branch_id', 'in', record.branch_ids.ids))
    
            initial_lines = self.env['account.move.line'].search(initial_domain)
            record.initial_balance = sum(line.balance for line in initial_lines)
    
            # حساب الحركات خلال الفترة
            period_domain = [
                ('date', '>=', record.date_from),
                ('date', '<=', record.date_to),
                ('partner_id', '=', record.partner_id.id),
                ('company_id', '=', record.company_id.id),
                ('move_id.state', '=', 'posted'),
                ('account_id.account_type', '=', 'asset_receivable')
            ]
            if record.branch_ids:
                period_domain.append(('branch_id', 'in', record.branch_ids.ids))
    
            period_lines = self.env['account.move.line'].search(period_domain)
            
            # حساب إجمالي الفواتير (فواتير بيع)
            invoice_domain = period_domain + [
                ('move_id.move_type', 'in', ['out_invoice', 'out_refund', 'out_receipt'])
            ]
            invoice_lines = self.env['account.move.line'].search(invoice_domain)
            record.total_invoices = sum(line.balance for line in invoice_lines if line.move_id.move_type == 'out_invoice')
            record.total_refunds = sum(line.balance for line in invoice_lines if line.move_id.move_type == 'out_refund')
            
            # حساب إجمالي المقبوضات
            payment_domain = period_domain + [
                ('payment_id', '!=', False)
            ]
            payment_lines = self.env['account.move.line'].search(payment_domain)
            record.total_payments = sum(line.balance for line in payment_lines)
            
            # حساب المدين والدائن بشكل صحيح
            record.total_debit = sum(line.debit for line in period_lines)
            record.total_credit = sum(line.credit for line in period_lines)
    
            # حساب الرصيد الختامي بشكل صحيح
            record.final_balance = record.initial_balance + sum(line.balance for line in period_lines)

    @api.depends('date_from', 'date_to', 'partner_id', 'company_id', 'branch_ids')
    def _compute_transaction_lines(self):
        for record in self:
            # إنشاء جدول HTML لعرض الحركات
            html_lines = []
            html_lines.append("""
                <style>
                    .total-row { background-color: #f2f2f2; font-weight: bold; }
                    .section-row { background-color: #e6f2ff; font-weight: bold; }
                    .table { width: 100%; border-collapse: collapse; direction: rtl; }
                    .table th { padding: 8px; border: 1px solid #ddd; background-color: #4472C4; color: white; }
                    .table td { padding: 8px; border: 1px solid #ddd; }
                    .text-right { text-align: right; }
                    .text-center { text-align: center; }
                    .document-link { color: #4472C4; text-decoration: none; }
                    .document-link:hover { text-decoration: underline; }
                </style>
                <table class="table">
                    <thead>
                        <tr>
                            <th>الرصيد</th>
                            <th>دائن</th>
                            <th>مدين</th>
                            <th>نوع الحركة</th>
                            <th>الرقم</th>
                            <th>التاريخ</th>
                        </tr>
                    </thead>
                    <tbody>
            """)

            # إضافة الرصيد الافتتاحي
            html_lines.append(f"""
                <tr class="total-row">
                    <td class="text-right">{format(record.initial_balance, '.2f')}</td>
                    <td class="text-right"></td>
                    <td class="text-right"></td>
                    <td></td>
                    <td></td>
                    <td>{record.date_from}</td>
                </tr>
            """)

            running_balance = record.initial_balance
            
            # البحث عن جميع حركات الحساب وترتيبها حسب التاريخ تصاعدياً
            domain = [
                ('date', '>=', record.date_from),
                ('date', '<=', record.date_to),
                ('partner_id', '=', record.partner_id.id),
                ('company_id', '=', record.company_id.id),
                ('move_id.state', '=', 'posted'),
                ('account_id.account_type', '=', 'asset_receivable')
            ]
            if record.branch_ids:
                domain.append(('branch_id', 'in', record.branch_ids.ids))
    
            lines = self.env['account.move.line'].search(domain, order='date, move_id, id')
            
            # تجميع الحركات حسب المستند
            move_dict = defaultdict(lambda: {
                'debit': 0.0, 
                'credit': 0.0, 
                'name': '', 
                'date': False, 
                'branch': '',
                'move_type': '',
                'doc_number': '',
                'doc_type': '',
                'move_id': False
            })
            
            for line in lines:
                move = line.move_id
                doc_type = ''
                if move.move_type == 'out_invoice':
                    doc_type = 'فاتورة بيع'
                elif move.move_type == 'out_refund':
                    doc_type = 'إشعار دائن'
                elif move.payment_id:
                    doc_type = 'مقبوضات'
                else:
                    doc_type = 'حركة أخرى'
                
                move_dict[move]['debit'] += line.debit
                move_dict[move]['credit'] += line.credit
                if not move_dict[move]['name']:
                    move_dict[move]['name'] = line.name or ''
                if not move_dict[move]['date']:
                    move_dict[move]['date'] = line.date
                if not move_dict[move]['branch']:
                    move_dict[move]['branch'] = line.branch_id.name or ''
                if not move_dict[move]['doc_type']:
                    move_dict[move]['doc_type'] = doc_type
                if not move_dict[move]['doc_number']:
                    move_dict[move]['doc_number'] = move.name or ''
                if not move_dict[move]['move_id']:
                    move_dict[move]['move_id'] = move.id
            
            # دمج جميع الحركات في قائمة واحدة وترتيبها حسب التاريخ
            all_moves = []
            for move, vals in move_dict.items():
                all_moves.append({
                    'date': vals['date'],
                    'doc_number': vals['doc_number'],
                    'name': vals['name'],
                    'doc_type': vals['doc_type'],
                    'debit': vals['debit'],
                    'credit': vals['credit'],
                    'balance': vals['debit'] - vals['credit'],
                    'move_id': vals['move_id']
                })
            
            # ترتيب الحركات حسب التاريخ تصاعدياً
            all_moves.sort(key=lambda x: x['date'])
            
            # عرض جميع الحركات معاً بعد الترتيب
            for move in all_moves:
                running_balance += move['balance']  # تحديث الرصيد المتراكم بشكل صحيح
                
                # إنشاء رابط للمستند
                doc_link = f"/web#id={move['move_id']}&model=account.move&view_type=form"
                
                html_lines.append(f"""
                    <tr>
                        <td class="text-right">{format(running_balance, '.2f')}</td>
                        <td class="text-right">{format(move['credit'], '.2f') if move['credit'] > 0 else ''}</td>
                        <td class="text-right">{format(move['debit'], '.2f') if move['debit'] > 0 else ''}</td>
                        <td>{move['doc_type']}</td>
                        <td><a href="{doc_link}" class="document-link">{move['doc_number']}</a></td>
                        <td>{move['date']}</td>
                    </tr>
                """)

            
            # إجمالي عام
            html_lines.append(f"""
                <tr class="total-row">
                    <td class="text-right">{format(record.final_balance, '.2f')}</td>
                    <td class="text-right">{format(record.total_credit, '.2f')}</td>
                    <td class="text-right">{format(record.total_debit, '.2f')}</td>
                    <td colspan="3">الإجمالي العام للفترة</td>
                </tr>
            """)

            html_lines.append("""
                    </tbody>
                </table>
            """)

            record.transaction_lines = '\n'.join(html_lines)

    def generate_account_statement_report(self):
        """إنشاء تقرير Excel لكشف حساب العميل"""
        self.ensure_one()
        # إنشاء كتاب Excel
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True, 'right_to_left': True})
        worksheet = workbook.add_worksheet('كشف حساب العميل')
        worksheet.right_to_left()
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
        section_format = workbook.add_format({
            'bold': True, 'align': 'right', 'border': 1,
            'bg_color': '#E6F2FF'
        })
        date_format = workbook.add_format({
            'num_format': 'yyyy-mm-dd',
            'border': 1,
            'align': 'right'
        })
        # إضافة شعار الشركة
        row = 0
        if self.company_id.logo:
            try:
                image_data = io.BytesIO(base64.b64decode(self.company_id.logo))
                worksheet.merge_range(row, 3, row+1, 3, '')
                worksheet.insert_image(row, 3, 'logo.png', {
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
                logger.error(f"Failed to insert company logo: {str(e)}")
                pass
    
        # إضافة عنوان التقرير
        worksheet.merge_range(row, 0, row, 6, 'كشف حساب العميل', title_format)
        row += 1
        worksheet.merge_range(row, 0, row, 6, f'العميل: {self.partner_id.name}', 
                             workbook.add_format({'align': 'center', 'font_size': 12}))
        row += 1
        worksheet.merge_range(row, 0, row, 6, f'من {self.date_from} إلى {self.date_to}', 
                             workbook.add_format({'align': 'center', 'font_size': 12}))
        row += 2
    
        # إضافة معلومات الرصيد
        worksheet.write(row, 0, 'الرصيد الافتتاحي', label_format)
        worksheet.write(row, 1, round(self.initial_balance, 2), currency_format)
        row += 1
        
        worksheet.write(row, 0, 'إجمالي الفواتير', label_format)
        worksheet.write(row, 1, round(self.total_invoices, 2), currency_format)
        row += 1
        
        worksheet.write(row, 0, 'إجمالي الإشعارات الدائنة', label_format)
        worksheet.write(row, 1, round(self.total_refunds, 2), currency_format)
        row += 1
        
        worksheet.write(row, 0, 'إجمالي المقبوضات', label_format)
        worksheet.write(row, 1, round(self.total_payments, 2), currency_format)
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
            'نوع الحركة',
            'مدين',
            'دائن',
            'الرصيد'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(row, col, header, header_format)
        row += 1
    
        # إضافة الرصيد الافتتاحي
        worksheet.write(row, 0, self.date_from, date_format)
        worksheet.write(row, 1, '', text_format)
        worksheet.write(row, 2, '', text_format)
        worksheet.write(row, 3, '', currency_format)
        worksheet.write(row, 4, '', currency_format)
        worksheet.write(row, 5, round(self.initial_balance, 2), currency_format)
        row += 1
    
        running_balance = self.initial_balance
        
        # البحث عن جميع حركات الحساب وترتيبها حسب التاريخ تصاعدياً
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('partner_id', '=', self.partner_id.id),
            ('company_id', '=', self.company_id.id),
            ('move_id.state', '=', 'posted'),
            ('account_id.account_type', '=', 'asset_receivable')
        ]
        if self.branch_ids:
            domain.append(('branch_id', 'in', self.branch_ids.ids))
    
        lines = self.env['account.move.line'].search(domain, order='date, move_id, id')
        
        # تجميع الحركات حسب المستند
        move_dict = defaultdict(lambda: {
            'debit': 0.0, 
            'credit': 0.0, 
            'name': '', 
            'date': False, 
            'branch': '',
            'move_type': '',
            'doc_number': '',
            'doc_type': ''
        })
        
        for line in lines:
            move = line.move_id
            doc_type = ''
            if move.move_type == 'out_invoice':
                doc_type = 'فاتورة بيع'
            elif move.move_type == 'out_refund':
                doc_type = 'إشعار دائن'
            elif move.payment_id:
                doc_type = 'مقبوضات'
            else:
                doc_type = 'حركة أخرى'
            
            move_dict[move]['debit'] += line.debit
            move_dict[move]['credit'] += line.credit
            if not move_dict[move]['name']:
                move_dict[move]['name'] = line.name or ''
            if not move_dict[move]['date']:
                move_dict[move]['date'] = line.date
            if not move_dict[move]['branch']:
                move_dict[move]['branch'] = line.branch_id.name or ''
            if not move_dict[move]['doc_type']:
                move_dict[move]['doc_type'] = doc_type
            if not move_dict[move]['doc_number']:
                move_dict[move]['doc_number'] = move.name or ''
        
        # دمج جميع الحركات في قائمة واحدة وترتيبها حسب التاريخ
        all_moves = []
        for move, vals in move_dict.items():
            all_moves.append({
                'date': vals['date'],
                'doc_number': vals['doc_number'],
                'name': vals['name'],
                'doc_type': vals['doc_type'],
                'debit': vals['debit'],
                'credit': vals['credit']
            })
        
        # ترتيب الحركات حسب التاريخ تصاعدياً
        all_moves.sort(key=lambda x: x['date'])
        
        # عرض جميع الحركات معاً بعد الترتيب
        for move in all_moves:
            if move['debit'] > 0:
                running_balance += move['debit']
            else:
                running_balance -= move['credit']
                
            worksheet.write(row, 0, move['date'], date_format)
            worksheet.write(row, 1, move['doc_number'], text_format)
            worksheet.write(row, 2, move['doc_type'], text_format)
            worksheet.write(row, 3, round(move['debit'], 2) if move['debit'] > 0 else '', currency_format)
            worksheet.write(row, 4, round(move['credit'], 2) if move['credit'] > 0 else '', currency_format)
            worksheet.write(row, 5, round(running_balance, 2), currency_format)
            row += 1
        
        # إجمالي عام
        worksheet.write(row, 0, 'الإجمالي العام للفترة', total_format)
        worksheet.write(row, 1, '', total_format)
        worksheet.write(row, 2, '', total_format)
        worksheet.write(row, 3, round(self.total_debit, 2), total_format)
        worksheet.write(row, 4, round(self.total_credit, 2), total_format)
        worksheet.write(row, 5, round(self.final_balance, 2), total_format)
        row += 1
    
        # ضبط عرض الأعمدة
        worksheet.set_column(0, 0, 12)  # التاريخ
        worksheet.set_column(1, 1, 15)  # الرقم
        worksheet.set_column(2, 2, 15)  # نوع الحركة
        worksheet.set_column(3, 5, 15)  # الأرقام
    
        # إغلاق الكتاب وحفظه
        workbook.close()
        output.seek(0)
    
        return {
            'file_name': f"كشف_حساب_{self.partner_id.name}_{self.date_from}_إلى_{self.date_to}.xlsx",
            'file_content': output.read(),
            'file_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }

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
        action = self.env.ref('account.action_account_moves_all').read()[0]
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('partner_id', '=', self.partner_id.id),
            ('company_id', '=', self.company_id.id),
            ('move_id.state', '=', 'posted')
        ]
        if self.branch_ids:
            domain.append(('branch_id', 'in', self.branch_ids.ids))
        action['domain'] = domain
        action['context'] = {
            'search_default_partner_id': self.partner_id.id,
            'create': False
        }
        return action

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
            logger.error("Failed to generate account statement report: %s", str(e))
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
                logger.warning("Failed to register Arabic font, using default")
            
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
            
            section_style = ParagraphStyle(
                'Section',
                parent=styles['Normal'],
                fontName='Arabic',
                fontSize=10,
                alignment=2,  # 2=right
                fontWeight='bold',
                backColor=colors.HexColor('#E6F2FF')
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
                ['إجمالي الإشعارات الدائنة', format(round(self.total_refunds, 2), ',.2f')],
                ['إجمالي المقبوضات', format(round(self.total_payments, 2), ',.2f')],
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
                'نوع الحركة',
                'مدين',
                'دائن',
                'الرصيد'
            ]
            
            transaction_data = [transaction_header]
            
            # إضافة الرصيد الافتتاحي
            transaction_data.append([
                self.date_from.strftime('%Y-%m-%d'),
                '',
                '',
                '',
                '',
                format(round(self.initial_balance, 2), ',.2f')
            ])
            
            running_balance = self.initial_balance
            
            # البحث عن جميع حركات الحساب وترتيبها حسب التاريخ تصاعدياً
            domain = [
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
                ('partner_id', '=', self.partner_id.id),
                ('company_id', '=', self.company_id.id),
                ('move_id.state', '=', 'posted'),
                ('account_id.account_type', '=', 'asset_receivable')
            ]
            if self.branch_ids:
                domain.append(('branch_id', 'in', self.branch_ids.ids))

            lines = self.env['account.move.line'].search(domain, order='date, move_id, id')
            
            # تجميع الحركات حسب المستند
            move_dict = defaultdict(lambda: {
                'debit': 0.0, 
                'credit': 0.0, 
                'name': '', 
                'date': False, 
                'branch': '',
                'move_type': '',
                'doc_number': '',
                'doc_type': ''
            })
            
            for line in lines:
                move = line.move_id
                doc_type = ''
                if move.move_type == 'out_invoice':
                    doc_type = 'فاتورة بيع'
                elif move.move_type == 'out_refund':
                    doc_type = 'إشعار دائن'
                elif move.payment_id:
                    doc_type = 'مقبوضات'
                else:
                    doc_type = 'حركة أخرى'
                
                move_dict[move]['debit'] += line.debit
                move_dict[move]['credit'] += line.credit
                if not move_dict[move]['name']:
                    move_dict[move]['name'] = line.name or ''
                if not move_dict[move]['date']:
                    move_dict[move]['date'] = line.date
                if not move_dict[move]['branch']:
                    move_dict[move]['branch'] = line.branch_id.name or ''
                if not move_dict[move]['doc_type']:
                    move_dict[move]['doc_type'] = doc_type
                if not move_dict[move]['doc_number']:
                    move_dict[move]['doc_number'] = move.name or ''
            
            # دمج جميع الحركات في قائمة واحدة وترتيبها حسب التاريخ
            all_moves = []
            for move, vals in move_dict.items():
                all_moves.append({
                    'date': vals['date'],
                    'doc_number': vals['doc_number'],
                    'name': vals['name'],
                    'doc_type': vals['doc_type'],
                    'debit': vals['debit'],
                    'credit': vals['credit']
                })
            
            # ترتيب الحركات حسب التاريخ تصاعدياً
            all_moves.sort(key=lambda x: x['date'])
            
            # عرض جميع الحركات معاً بعد الترتيب
            for move in all_moves:
                if move['debit'] > 0:
                    running_balance += move['debit']
                else:
                    running_balance -= move['credit']
                    
                transaction_data.append([
                    move['date'].strftime('%Y-%m-%d'),
                    move['doc_number'],
                    move['doc_type'],
                    format(round(move['debit'], 2), ',.2f') if move['debit'] > 0 else '',
                    format(round(move['credit'], 2), ',.2f') if move['credit'] > 0 else '',
                    format(round(running_balance, 2), ',.2f')
                ])
            
            # إجمالي عام
            transaction_data.append([
                'الإجمالي العام للفترة', '', '',
                format(round(self.total_debit, 2), ',.2f'),
                format(round(self.total_credit, 2), ',.2f'),
                format(round(self.final_balance, 2), ',.2f')
            ])
            
            # إنشاء جدول الحركات
            transaction_table = Table(transaction_data, colWidths=[70, 70, 70, 70, 70, 70])
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
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#D9E1F2')),
                ('FONTWEIGHT', (0, -1), (-1, -1), 'BOLD')
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
            logger.error("Failed to generate PDF report: %s", str(e))
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
            logger.error("Failed to generate PDF report: %s", str(e))
            raise
