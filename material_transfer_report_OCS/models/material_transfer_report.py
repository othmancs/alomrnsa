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


class MaterialTransferReport(models.Model):
    _name = 'material.transfer.report'
    _description = 'تقرير طلبات النقل بين الفروع'
    _rec_name = 'date_from'
    _order = 'date_from desc'

    date_from = fields.Date(string='من تاريخ', default=fields.Date.today(), required=True)
    date_to = fields.Date(string='إلى تاريخ', default=fields.Date.today(), required=True)
    company_id = fields.Many2one(
        'res.company', string='الشركة',
        default=lambda self: self.env.company, required=True
    )
    branch_from_id = fields.Many2one(
        'res.branch',
        string='من فرع'
    )
    branch_to_id = fields.Many2one(
        'res.branch',
        string='إلى فرع'
    )

    @api.onchange('date_from')
    def _onchange_date_from(self):
        if self.date_from and not self.date_to:
            self.date_to = self.date_from

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_from and record.date_to and record.date_from > record.date_to:
                raise models.ValidationError("تاريخ البداية يجب أن يكون قبل تاريخ النهاية")

    def get_transfer_data(self):
        """جمع بيانات طلبات النقل بين الفروع"""
        self.ensure_one()
        
        domain = [
            ('state', '=', 'approved'),
            ('request_date', '>=', self.date_from),
            ('request_date', '<=', self.date_to),
            ('company_id', '=', self.company_id.id)
        ]
        
        if self.branch_from_id:
            domain.append(('branch_from_id', '=', self.branch_from_id.id))
        if self.branch_to_id:
            domain.append(('branch_to_id', '=', self.branch_to_id.id))
        
        transfers = self.env['material.request'].search(domain)
        
        result = []
        for transfer in transfers:
            for line in transfer.line_ids:
                # البحث عن عمليات النقل المرتبطة بهذا الطلب
                pickings = self.env['stock.picking'].search([
                    ('material_request_id', '=', transfer.id),
                    ('state', '=', 'done')
                ])
                
                # حساب الكمية المستلمة
                received_qty = 0.0
                for picking in pickings:
                    for move in picking.move_lines:
                        if move.product_id == line.product_id:
                            received_qty += move.quantity_done
                
                # حساب الكمية المتاحة في الفرع المصدر
                qty_available_from = line.product_id.with_context(
                    location=transfer.branch_from_id.warehouse_id.lot_stock_id.id
                ).qty_available
                
                # حساب الكمية المتاحة في الفرع الهدف
                qty_available_to = line.product_id.with_context(
                    location=transfer.branch_to_id.warehouse_id.lot_stock_id.id
                ).qty_available if transfer.branch_to_id.warehouse_id else 0.0
                
                # حساب الفرق بين الكمية المرسلة والمستلمة
                difference = line.qty - received_qty
                
                result.append({
                    'transfer': transfer.name,
                    'date': transfer.request_date,
                    'branch_from': transfer.branch_from_id.name,
                    'branch_to': transfer.branch_to_id.name,
                    'product': line.product_id.name,
                    'product_code': line.product_id.default_code,
                    'requested_qty': line.qty,
                    'qty_available_from': qty_available_from,
                    'qty_available_to': qty_available_to,
                    'sent_qty': line.qty,  # الكمية المعتمدة تعتبر مرسلة
                    'received_qty': received_qty,
                    'difference': difference,
                    'uom': line.uom_id.name,
                })
        
        return result

    def generate_excel_report(self):
        """إنشاء تقرير Excel لطلبات النقل بين الفروع"""
        self.ensure_one()
        
        # إنشاء كتاب Excel
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True, 'right_to_left': True})
        worksheet = workbook.add_worksheet('تقرير طلبات النقل')
        
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
        number_format = workbook.add_format({
            'num_format': '#,##0.00', 'border': 1, 'align': 'right'
        })
        text_format = workbook.add_format({'border': 1, 'align': 'right'})
        total_format = workbook.add_format({
            'bold': True, 'num_format': '#,##0.00', 'border': 1,
            'align': 'right', 'bg_color': '#D9E1F2'
        })
        
        # إضافة عنوان التقرير
        worksheet.merge_range(0, 0, 0, 9, 'تقرير طلبات النقل بين الفروع', title_format)
        worksheet.merge_range(1, 0, 1, 9, f'من {self.date_from} إلى {self.date_to}', 
                             workbook.add_format({'align': 'center', 'font_size': 12}))
        
        # إضافة شعار الشركة
        if self.company_id.logo:
            try:
                image_data = io.BytesIO(base64.b64decode(self.company_id.logo))
                worksheet.insert_image(0, 8, 'logo.png', {
                    'image_data': image_data,
                    'x_scale': 0.15, 
                    'y_scale': 0.15,
                    'object_position': 3
                })
            except Exception as e:
                _logger.error(f"Failed to insert company logo: {str(e)}")
        
        # عناوين الأعمدة
        headers = [
            'رقم الطلب',
            'التاريخ',
            'من فرع',
            'إلى فرع',
            'كود المنتج',
            'المنتج',
            'الكمية المطلوبة',
            'الكمية المصدر',
            'الكمية الهدف',
            'الكمية المرسلة',
            'الكمية المستقبلة',
            'الفرق',
            'وحدة القياس'
        ]
        
        # كتابة عناوين الأعمدة
        for col, header in enumerate(headers):
            worksheet.write(3, col, header, header_format)
        
        # جلب البيانات
        data = self.get_transfer_data()
        
        # كتابة البيانات
        row = 4
        for item in data:
            worksheet.write(row, 0, item['transfer'], text_format)
            worksheet.write(row, 1, item['date'], text_format)
            worksheet.write(row, 2, item['branch_from'], text_format)
            worksheet.write(row, 3, item['branch_to'], text_format)
            worksheet.write(row, 4, item['product_code'], text_format)
            worksheet.write(row, 5, item['product'], text_format)
            worksheet.write(row, 6, item['requested_qty'], number_format)
            worksheet.write(row, 7, item['qty_available_from'], number_format)
            worksheet.write(row, 8, item['qty_available_to'], number_format)
            worksheet.write(row, 9, item['sent_qty'], number_format)
            worksheet.write(row, 10, item['received_qty'], number_format)
            worksheet.write(row, 11, item['difference'], number_format)
            worksheet.write(row, 12, item['uom'], text_format)
            row += 1
        
        # إضافة الإجماليات
        if data:
            worksheet.write(row, 5, 'الإجمالي:', header_format)
            worksheet.write(row, 6, sum(item['requested_qty'] for item in data), total_format)
            worksheet.write(row, 7, sum(item['qty_available_from'] for item in data), total_format)
            worksheet.write(row, 8, sum(item['qty_available_to'] for item in data), total_format)
            worksheet.write(row, 9, sum(item['sent_qty'] for item in data), total_format)
            worksheet.write(row, 10, sum(item['received_qty'] for item in data), total_format)
            worksheet.write(row, 11, sum(item['difference'] for item in data), total_format)
        
        # ضبط عرض الأعمدة
        col_widths = [15, 12, 15, 15, 15, 30, 15, 15, 15, 15, 15, 15, 15]
        for col, width in enumerate(col_widths):
            worksheet.set_column(col, col, width)
        
        # إغلاق الكتاب وحفظه
        workbook.close()
        output.seek(0)
        
        return {
            'file_name': f"تقرير_طلبات_النقل_{self.date_from}_إلى_{self.date_to}.xlsx",
            'file_content': output.read(),
            'file_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }

    def generate_pdf_report(self):
        """إنشاء تقرير PDF لطلبات النقل بين الفروع"""
        self.ensure_one()
        
        # إنشاء مستند PDF
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=landscape(letter), rightMargin=40, leftMargin=40, topMargin=60, bottomMargin=40)
        
        # أنماط النص
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.white,
            alignment=1,  # 0=Left, 1=Center, 2=Right
            spaceAfter=6,
            backColor=colors.HexColor('#4472C4')
        )
        normal_style = styles['Normal']
        normal_style.alignment = 2  # محاذاة لليمين للنصوص العربية
        
        # محتوى التقرير
        elements = []
        
        # عنوان التقرير
        title = Paragraph("تقرير طلبات النقل بين الفروع", title_style)
        elements.append(title)
        
        # تاريخ التقرير
        date_range = Paragraph(f"من {self.date_from} إلى {self.date_to}", normal_style)
        elements.append(date_range)
        
        # إضافة شعار الشركة
        if self.company_id.logo:
            try:
                logo_data = io.BytesIO(base64.b64decode(self.company_id.logo))
                logo = Image(logo_data, width=1.5*inch, height=0.5*inch)
                logo.hAlign = 'RIGHT'
                elements.append(logo)
            except Exception as e:
                _logger.error(f"Failed to insert company logo in PDF: {str(e)}")
        
        elements.append(Spacer(1, 0.25*inch))
        
        # جلب البيانات
        data = self.get_transfer_data()
        
        # عناوين الأعمدة
        headers = [
            'رقم الطلب',
            'التاريخ',
            'من فرع',
            'إلى فرع',
            'كود المنتج',
            'المنتج',
            'المطلوب',
            'المصدر',
            'الهدف',
            'المرسلة',
            'المستلمة',
            'الفرق',
            'الوحدة'
        ]
        
        # تحضير بيانات الجدول
        table_data = [headers]
        
        for item in data:
            row = [
                item['transfer'],
                item['date'].strftime('%Y-%m-%d') if item['date'] else '',
                item['branch_from'],
                item['branch_to'],
                item['product_code'],
                item['product'],
                f"{item['requested_qty']:.2f}",
                f"{item['qty_available_from']:.2f}",
                f"{item['qty_available_to']:.2f}",
                f"{item['sent_qty']:.2f}",
                f"{item['received_qty']:.2f}",
                f"{item['difference']:.2f}",
                item['uom']
            ]
            table_data.append(row)
        
        # إنشاء الجدول
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(table)
        
        # إضافة الإجماليات إذا وجدت بيانات
        if data:
            totals = [
                '',
                '',
                '',
                '',
                '',
                'الإجمالي:',
                f"{sum(item['requested_qty'] for item in data):.2f}",
                f"{sum(item['qty_available_from'] for item in data):.2f}",
                f"{sum(item['qty_available_to'] for item in data):.2f}",
                f"{sum(item['sent_qty'] for item in data):.2f}",
                f"{sum(item['received_qty'] for item in data):.2f}",
                f"{sum(item['difference'] for item in data):.2f}",
                ''
            ]
            
            total_table = Table([totals], colWidths=[doc.width/len(headers)]*len(headers))
            total_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D9E1F2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, 0), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, 0), 1, colors.black),
            ]))
            
            elements.append(total_table)
        
        # بناء المستند
        doc.build(elements)
        output.seek(0)
        
        return {
            'file_name': f"تقرير_طلبات_النقل_{self.date_from}_إلى_{self.date_to}.pdf",
            'file_content': output.read(),
            'file_type': 'application/pdf'
        }

    def action_generate_excel_report(self):
        """إجراء لإنشاء وتنزيل التقرير"""
        self.ensure_one()
        try:
            report_data = self.generate_excel_report()
            
            # إنشاء مرفق (attachment) للتقرير
            attachment = self.env['ir.attachment'].create({
                'name': report_data['file_name'],
                'datas': base64.b64encode(report_data['file_content']),
                'res_model': 'material.transfer.report',
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
            _logger.error("Failed to generate transfer report: %s", str(e))
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
                'res_model': 'material.transfer.report',
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