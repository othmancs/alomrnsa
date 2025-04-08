# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
from collections import defaultdict
import base64
import io
import xlsxwriter

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
        help='إذا لم يتم تحديد أي فرع، سيتم عرض جميع الفروع'
    )
    company_currency_id = fields.Many2one(
        'res.currency', string='العملة',
        related='company_id.currency_id', store=True
    )
    excel_file = fields.Binary(string='تقرير Excel')
    file_name = fields.Char(string='اسم الملف')

    # الحقول المحسوبة
    cash_sales = fields.Monetary(
        string='مبيعات نقدية مدفوعة بتاريخه قبل الضريبة',
        currency_field='company_currency_id',
        compute='_compute_sales_totals', store=True,
        default=0.0
    )
    total_tax = fields.Monetary(
        string='مجموع الضريبة فقط',
        currency_field='company_currency_id',
        compute='_compute_sales_totals', store=True,
        default=0.0
    )
    partial_sales = fields.Monetary(
        string='مبيعات مدفوع جزئي',
        currency_field='company_currency_id',
        compute='_compute_sales_totals', store=True,
        default=0.0
    )
    credit_sales = fields.Monetary(
        string='مبيعات آجلة غير مدفوعة',
        currency_field='company_currency_id',
        compute='_compute_sales_totals', store=True,
        default=0.0
    )
    cash_refunds = fields.Monetary(
        string='إرجاعات مسترد المبلغ',
        currency_field='company_currency_id',
        compute='_compute_refund_totals', store=True,
        default=0.0
    )
    credit_refunds = fields.Monetary(
        string='إرجاعات غير مسترد المبلغ',
        currency_field='company_currency_id',
        compute='_compute_refund_totals', store=True,
        default=0.0
    )
    cash_box = fields.Monetary(
        string='المقبوضات',
        currency_field='company_currency_id',
        compute='_compute_cash_box', store=True,
        default=0.0
    )
    total_cash = fields.Monetary(
        string='إجمالي الصندوق',
        currency_field='company_currency_id',
        compute='_compute_total_cash', store=True,
        default=0.0
    )
    payment_method_totals = fields.Html(
        string='المجاميع حسب طريقة الدفع',
        compute='_compute_payment_method_totals',
        sanitize=False,
        default=''
    )
    branch_totals = fields.Html(
        string='المجاميع حسب الفرع',
        compute='_compute_branch_totals',
        sanitize=False,
        default=''
    )

    def action_generate_excel(self):
        self.ensure_one()
        output = io.BytesIO()
        
        # إنشاء ملف Excel
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('تقرير المبيعات')
        
        # تنسيقات الخلايا
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1,
            'font_size': 12
        })
        
        currency_format = workbook.add_format({
            'num_format': '#,##0.00',
            'align': 'right'
        })
        
        # كتابة العنوان الرئيسي
        title_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 14
        })
        
        worksheet.merge_range('A1:I1', 'تقرير ملخص حركة المبيعات اليومية', title_format)
        worksheet.write('A2', 'من تاريخ:')
        worksheet.write('B2', self.date_from.strftime('%Y-%m-%d'))
        worksheet.write('A3', 'إلى تاريخ:')
        worksheet.write('B3', self.date_to.strftime('%Y-%m-%d'))
        
        # عناوين الأعمدة
        columns = [
            'الفرع',
            'مبيعات نقدية',
            'الضريبة',
            'مبيعات جزئية',
            'مبيعات آجلة',
            'مرتجعات نقدية',
            'مرتجعات آجلة',
            'المقبوضات',
            'إجمالي الصندوق'
        ]
        
        for col_num, column_title in enumerate(columns):
            worksheet.write(4, col_num, column_title, header_format)
        
        # الحصول على بيانات الفروع
        branches = self.branch_ids or self.env['res.branch'].search([('company_id', '=', self.company_id.id)])
        row_num = 5
        
        for branch in branches:
            # حساب البيانات لكل فرع
            branch_data = self._get_branch_data(branch)
            
            # كتابة بيانات الفرع في Excel
            worksheet.write(row_num, 0, branch.name)
            worksheet.write(row_num, 1, branch_data['cash_sales'], currency_format)
            worksheet.write(row_num, 2, branch_data['total_tax'], currency_format)
            worksheet.write(row_num, 3, branch_data['partial_sales'], currency_format)
            worksheet.write(row_num, 4, branch_data['credit_sales'], currency_format)
            worksheet.write(row_num, 5, branch_data['cash_refund'], currency_format)
            worksheet.write(row_num, 6, branch_data['credit_refund'], currency_format)
            worksheet.write(row_num, 7, branch_data['cash_box'], currency_format)
            worksheet.write(row_num, 8, branch_data['total_cash'], currency_format)
            
            row_num += 1
        
        # إضافة الإجماليات
        if branches:
            worksheet.write(row_num, 0, 'الإجمالي', header_format)
            for col_num in range(1, 9):
                start_row = 5
                end_row = row_num - 1
                worksheet.write_formula(
                    row_num, col_num,
                    f'=SUM({xl_col_to_name(col_num)}{start_row+1}:{xl_col_to_name(col_num)}{end_row+1})',
                    currency_format
                )
        
        # ضبط عرض الأعمدة
        worksheet.set_column('A:A', 30)
        for col in ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']:
            worksheet.set_column(f'{col}:{col}', 15)
        
        workbook.close()
        output.seek(0)
        
        # حفظ الملف في السجل
        file_name = f'daily_sales_summary_{self.date_from.strftime("%Y-%m-%d")}_to_{self.date_to.strftime("%Y-%m-%d")}.xlsx'
        self.write({
            'excel_file': base64.b64encode(output.read()),
            'file_name': file_name
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/?model=daily.sales.summary&id={self.id}&field=excel_file&filename_field=file_name&download=true',
            'target': 'self',
        }

    def _get_branch_data(self, branch):
        """حساب بيانات فرع معين"""
        # حساب المبيعات النقدية
        cash_domain = [
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', '=', 'paid'),
            ('company_id', '=', self.company_id.id),
            ('branch_id', '=', branch.id)
        ]
        cash_invoices = self.env['account.move'].search(cash_domain)
        cash_sales = sum(invoice.amount_untaxed or 0.0 for invoice in cash_invoices)
        total_tax = sum(invoice.amount_tax or 0.0 for invoice in cash_invoices)
        
        # حساب المبيعات المدفوعة جزئياً
        partial_domain = [
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', '=', 'partial'),
            ('company_id', '=', self.company_id.id),
            ('branch_id', '=', branch.id)
        ]
        partial_invoices = self.env['account.move'].search(partial_domain)
        partial_sales = sum((invoice.amount_total or 0.0) - (invoice.amount_residual or 0.0) for invoice in partial_invoices)
        
        # حساب المبيعات الآجلة
        credit_domain = [
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', '=', 'not_paid'),
            ('company_id', '=', self.company_id.id),
            ('branch_id', '=', branch.id)
        ]
        credit_invoices = self.env['account.move'].search(credit_domain)
        credit_sales = sum(invoice.amount_untaxed or 0.0 for invoice in credit_invoices)
        
        # حساب المرتجعات النقدية
        cash_refund_domain = [
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('move_type', '=', 'out_refund'),
            ('state', '=', 'posted'),
            ('payment_state', '=', 'paid'),
            ('company_id', '=', self.company_id.id),
            ('branch_id', '=', branch.id)
        ]
        cash_refunds = self.env['account.move'].search(cash_refund_domain)
        cash_refund = sum(refund.amount_untaxed or 0.0 for refund in cash_refunds)
        
        # حساب مرتجعات الآجل
        credit_refund_domain = [
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('move_type', '=', 'out_refund'),
            ('state', '=', 'posted'),
            ('payment_state', '=', 'not_paid'),
            ('company_id', '=', self.company_id.id),
            ('branch_id', '=', branch.id)
        ]
        credit_refunds = self.env['account.move'].search(credit_refund_domain)
        credit_refund = sum(refund.amount_untaxed or 0.0 for refund in credit_refunds)
        
        # حساب المقبوضات
        payment_domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('payment_type', '=', 'inbound'),
            ('state', '=', 'posted'),
            ('is_internal_transfer', '=', False),
            ('company_id', '=', self.company_id.id),
            ('branch_id', '=', branch.id)
        ]
        payments = self.env['account.payment'].search(payment_domain)
        cash_box = sum(payment.amount or 0.0 for payment in payments)
        total_cash = cash_box - cash_refund
        
        return {
            'cash_sales': cash_sales,
            'total_tax': total_tax,
            'partial_sales': partial_sales,
            'credit_sales': credit_sales,
            'cash_refund': cash_refund,
            'credit_refund': credit_refund,
            'cash_box': cash_box,
            'total_cash': total_cash
        }

    @api.depends('date_from', 'date_to', 'company_id', 'branch_ids')
    def _compute_branch_totals(self):
        for record in self:
            branches = record.branch_ids or self.env['res.branch'].search([('company_id', '=', record.company_id.id)])
            result = []
            
            for branch in branches:
                branch_data = record._get_branch_data(branch)
                
                if any(branch_data.values()):
                    branch_result = f"""
                    <tr>
                        <td><b>{branch.name}</b></td>
                        <td>{float(branch_data['cash_sales']):.2f}</td>
                        <td>{float(branch_data['total_tax']):.2f}</td>
                        <td>{float(branch_data['partial_sales']):.2f}</td>
                        <td>{float(branch_data['credit_sales']):.2f}</td>
                        <td>{float(branch_data['cash_refund']):.2f}</td>
                        <td>{float(branch_data['credit_refund']):.2f}</td>
                        <td>{float(branch_data['cash_box']):.2f}</td>
                        <td>{float(branch_data['total_cash']):.2f}</td>
                    </tr>
                    """
                    result.append(branch_result)
            
            if result:
                header = """
                <table class="table table-bordered" style="width:100%;">
                    <thead>
                        <tr style="background-color:#f5f5f5;">
                            <th style="padding:8px;text-align:right;">الفرع</th>
                            <th style="padding:8px;text-align:right;">مبيعات نقدية</th>
                            <th style="padding:8px;text-align:right;">الضريبة</th>
                            <th style="padding:8px;text-align:right;">مبيعات جزئية</th>
                            <th style="padding:8px;text-align:right;">مبيعات آجلة</th>
                            <th style="padding:8px;text-align:right;">مرتجعات نقدية</th>
                            <th style="padding:8px;text-align:right;">مرتجعات آجلة</th>
                            <th style="padding:8px;text-align:right;">المقبوضات</th>
                            <th style="padding:8px;text-align:right;">إجمالي الصندوق</th>
                        </tr>
                    </thead>
                    <tbody>
                """
                footer = """
                    </tbody>
                </table>
                """
                record.branch_totals = header + "".join(result) + footer
            else:
                record.branch_totals = "<div style='text-align:center;padding:20px;'>لا توجد بيانات للعرض</div>"

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
            record.cash_sales = sum(invoice.amount_untaxed or 0.0 for invoice in cash_invoices)
            record.total_tax = sum(invoice.amount_tax or 0.0 for invoice in cash_invoices)

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
            record.partial_sales = sum(
                (invoice.amount_total or 0.0) - (invoice.amount_residual or 0.0) 
                for invoice in partial_invoices
            )

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
            record.credit_sales = sum(invoice.amount_untaxed or 0.0 for invoice in credit_invoices)

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
            record.cash_refunds = sum(refund.amount_untaxed or 0.0 for refund in cash_refunds)

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
            record.credit_refunds = sum(refund.amount_untaxed or 0.0 for refund in credit_refunds)

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
            record.cash_box = sum(payment.amount or 0.0 for payment in payments)

    @api.depends('cash_sales', 'partial_sales', 'cash_refunds', 'cash_box')
    def _compute_total_cash(self):
        for record in self:
            record.total_cash = (record.cash_box or 0.0) - (record.cash_refunds or 0.0)

    @api.onchange('date_from')
    def _onchange_date_from(self):
        if self.date_from and not self.date_to:
            self.date_to = self.date_from

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_from and record.date_to and record.date_from > record.date_to:
                raise models.ValidationError("تاريخ البداية يجب أن يكون قبل تاريخ النهاية")

def xl_col_to_name(col):
    """تحويل رقم العمود إلى حرف Excel (A, B, ..., Z, AA, AB, ...)"""
    col_name = ''
    while col > 0:
        col -= 1
        col_name = chr(ord('A') + (col % 26)) + col_name
        col //= 26
    return col_name
