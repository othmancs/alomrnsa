# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import io
import xlsxwriter
import base64
from datetime import datetime


class CustomerStatementReport(models.Model):
    _name = 'customer.statement.report'
    _description = 'تقرير كشف حساب العميل'

    customer_id = fields.Many2one(
        'res.partner',
        string='العميل',
        required=True,
        domain=[('customer_rank', '>', 0)]
    )
    date_from = fields.Date(
        string='من تاريخ',
        required=True,
        default=lambda self: fields.Date.context_today(self)
    )
    date_to = fields.Date(
        string='إلى تاريخ',
        required=True,
        default=lambda self: fields.Date.context_today(self)
    )
    branch_id = fields.Many2one(
        'res.branch',
        string='الفرع'
    )
    payment_status = fields.Selection([
        ('all', 'الكل'),
        ('paid', 'مسددة'),
        ('not_paid', 'غير مسددة')
    ], string='حالة الدفع', default='all')
    excel_file = fields.Binary('ملف Excel')
    file_name = fields.Char('اسم الملف')

    # def _compute_opening_balance(self):
    #     """ حساب الرصيد الافتتاحي قبل تاريخ البداية """
    #     account_move_line = self.env['account.move.line']
    #     domain = [
    #         ('partner_id', '=', self.customer_id.id),
    #         ('date', '<', self.date_from),
    #         ('account_id.internal_type', 'in', ['receivable', 'payable']),
    #         ('parent_state', '=', 'posted')
    #     ]

    #     if self.branch_id:
    #         domain.append(('branch_id', '=', self.branch_id.id))

    #     lines = account_move_line.search(domain)
    #     return sum(lines.mapped('balance'))
    def _compute_opening_balance(self):
        """ حساب الرصيد الافتتاحي قبل تاريخ البداية """
        try:
            # المحاولة مع إعدادات الشركة الجديدة
            company = self.env.company
            recv_account = company.property_account_receivable_id
            pay_account = company.property_account_payable_id
            
            if not recv_account or not pay_account:
                # إذا لم توجد إعدادات، البحث عن الحسابات حسب النوع
                Account = self.env['account.account']
                recv_account = Account.search([('user_type_id.type', '=', 'receivable')], limit=1)
                pay_account = Account.search([('user_type_id.type', '=', 'payable')], limit=1)
                
            domain = [
                ('partner_id', '=', self.customer_id.id),
                ('date', '<', self.date_from),
                ('account_id', 'in', (recv_account + pay_account).ids),
                ('parent_state', '=', 'posted')
            ]
            
            if self.branch_id:
                domain.append(('branch_id', '=', self.branch_id.id))
                
            lines = account_move_line.search(domain)
            return sum(lines.mapped('balance'))
            
        except Exception as e:
            # تسجيل الخطأ في سجلات النظام
            _logger.error("Error computing opening balance: %s", str(e))
            return 0.0
    def _get_transactions(self):
        """ جلب جميع الحركات في الفترة المحددة """
        account_move_line = self.env['account.move.line']
        domain = [
            ('partner_id', '=', self.customer_id.id),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('account_id.internal_type', 'in', ['receivable', 'payable']),
            ('parent_state', '=', 'posted')
        ]

        if self.branch_id:
            domain.append(('branch_id', '=', self.branch_id.id))

        if self.payment_status == 'paid':
            domain.append(('full_reconcile_id', '!=', False))
        elif self.payment_status == 'not_paid':
            domain.append(('full_reconcile_id', '=', False))

        lines = account_move_line.search(domain, order='date, id asc')

        transactions = []
        opening_balance = self._compute_opening_balance()
        balance = opening_balance

        for line in lines:
            # حساب الرصيد الجديد
            balance += line.debit - line.credit

            # تحديد نوع الحركة
            move_type = ''
            if line.move_id.move_type in ('out_invoice', 'out_refund', 'out_receipt'):
                move_type = 'فاتورة بيع' if line.move_id.move_type == 'out_invoice' else 'إشعار دائن'
            elif line.move_id.move_type in ('in_invoice', 'in_refund', 'in_receipt'):
                move_type = 'فاتورة شراء' if line.move_id.move_type == 'in_invoice' else 'إشعار مدين'
            elif line.payment_id:
                move_type = 'دفعة'
            else:
                move_type = 'قيد محاسبي'

            transactions.append({
                'date': line.date,
                'move_date': line.move_id.date,
                'name': line.name or line.move_id.name,
                'move_type': move_type,
                'reference': line.move_id.name,
                'debit': line.debit,
                'credit': line.credit,
                'balance': balance,
                'move_id': line.move_id.id,
                'payment_status': 'مسددة' if line.full_reconcile_id else 'غير مسددة',
                'journal': line.journal_id.name,
                'currency': line.currency_id.name or line.company_id.currency_id.name,
                'amount_currency': line.amount_currency if line.currency_id else line.balance
            })

        return transactions

    def _compute_closing_balance(self, opening_balance, transactions):
        """ حساب الرصيد الختامي """
        if transactions:
            return transactions[-1]['balance']
        return opening_balance

    def get_report_data(self):
        """ تجميع بيانات التقرير """
        customer_data = {
            'name': self.customer_id.name,
            'ref': self.customer_id.ref or '-',
            'vat': self.customer_id.vat or '-',
            'branch': self.branch_id.name if self.branch_id else 'الفرع الرئيسي',
            'phone': self.customer_id.phone or '-',
            'email': self.customer_id.email or '-'
        }

        opening_balance = self._compute_opening_balance()
        transactions = self._get_transactions()
        closing_balance = self._compute_closing_balance(opening_balance, transactions)

        return {
            'customer': customer_data,
            'opening_balance': opening_balance,
            'transactions': transactions,
            'closing_balance': closing_balance,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'company': self.env.company,
            'current_date': fields.Date.context_today(self),
            'user': self.env.user
        }

    def print_pdf_report(self):
        """ طباعة التقرير PDF """
        data = self.get_report_data()
        return self.env.ref('customer_statement.action_report_customer_statement').report_action(self, data=data)

    def export_to_excel(self):
        """ تصدير التقرير إلى Excel """
        # تحضير البيانات
        report_data = self.get_report_data()

        # إنشاء ملف Excel
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('كشف حساب العميل')

        # تنسيقات الخلايا
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 12,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1
        })

        title_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 14
        })

        currency_format = workbook.add_format({
            'num_format': '#,##0.00',
            'align': 'right'
        })

        date_format = workbook.add_format({
            'num_format': 'yyyy-mm-dd',
            'align': 'center'
        })

        # كتابة عنوان التقرير
        worksheet.merge_range('A1:F1', 'كشف حساب العميل', title_format)

        # معلومات العميل
        worksheet.write(2, 0, 'اسم العميل:')
        worksheet.write(2, 1, report_data['customer']['name'])
        worksheet.write(3, 0, 'الرقم المرجعي:')
        worksheet.write(3, 1, report_data['customer']['ref'])
        worksheet.write(4, 0, 'الرقم الضريبي:')
        worksheet.write(4, 1, report_data['customer']['vat'])
        worksheet.write(5, 0, 'الفرع:')
        worksheet.write(5, 1, report_data['customer']['branch'])

        # فترة التقرير
        worksheet.write(2, 4, 'من تاريخ:')
        worksheet.write(2, 5, report_data['date_from'], date_format)
        worksheet.write(3, 4, 'إلى تاريخ:')
        worksheet.write(3, 5, report_data['date_to'], date_format)
        worksheet.write(4, 4, 'تاريخ الطباعة:')
        worksheet.write(4, 5, report_data['current_date'], date_format)

        # الرصيد الافتتاحي
        worksheet.write(7, 0, 'الرصيد الافتتاحي:')
        worksheet.write(7, 1, report_data['opening_balance'], currency_format)

        # رؤوس الأعمدة
        columns = [
            {'header': 'التاريخ', 'format': date_format},
            {'header': 'نوع الحركة'},
            {'header': 'الوصف'},
            {'header': 'المرجع'},
            {'header': 'مدين', 'format': currency_format},
            {'header': 'دائن', 'format': currency_format},
            {'header': 'الرصيد', 'format': currency_format},
            {'header': 'الحالة'},
            {'header': 'الدورة'},
            {'header': 'العملة'},
            {'header': 'المبلغ بالعملة', 'format': currency_format}
        ]

        # كتابة رؤوس الأعمدة
        for col_num, col_data in enumerate(columns):
            worksheet.write(9, col_num, col_data['header'], header_format)

        # كتابة بيانات الحركات
        row_num = 10
        for transaction in report_data['transactions']:
            worksheet.write(row_num, 0, transaction['date'], date_format)
            worksheet.write(row_num, 1, transaction['move_type'])
            worksheet.write(row_num, 2, transaction['name'])
            worksheet.write(row_num, 3, transaction['reference'])
            worksheet.write(row_num, 4, transaction['debit'], currency_format)
            worksheet.write(row_num, 5, transaction['credit'], currency_format)
            worksheet.write(row_num, 6, transaction['balance'], currency_format)
            worksheet.write(row_num, 7, transaction['payment_status'])
            worksheet.write(row_num, 8, transaction['journal'])
            worksheet.write(row_num, 9, transaction['currency'])
            worksheet.write(row_num, 10, transaction['amount_currency'], currency_format)
            row_num += 1

        # الرصيد الختامي
        worksheet.write(row_num + 1, 0, 'الرصيد الختامي:')
        worksheet.write(row_num + 1, 1, report_data['closing_balance'], currency_format)

        # ضبط عرض الأعمدة
        worksheet.set_column('A:A', 12)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 30)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:F', 15)
        worksheet.set_column('G:G', 20)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 15)
        worksheet.set_column('J:J', 10)
        worksheet.set_column('K:K', 15)

        workbook.close()
        output.seek(0)

        # حفظ الملف في السجل
        self.write({
            'excel_file': base64.b64encode(output.read()),
            'file_name': f"كشف_حساب_{report_data['customer']['name']}_{report_data['date_from']}_to_{report_data['date_to']}.xlsx"
        })

        # إرجاع إجراء لتحميل الملف
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/?model=customer.statement.report&id={self.id}&field=excel_file&filename={self.file_name}&download=true',
            'target': 'self',
        }

    def action_view_transaction(self, move_id):
        """ عرض الحركة المحددة """
        return {
            'type': 'ir.actions.act_window',
            'name': 'حركة',
            'res_model': 'account.move',
            'res_id': move_id,
            'view_mode': 'form',
            'target': 'current',
        }
