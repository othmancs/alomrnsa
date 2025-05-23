# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
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


    def _compute_opening_balance(self):
        """ حساب الرصيد الافتتاحي قبل تاريخ البداية """
        try:
            # الحصول على الحسابات الافتراضية للشركة
            company = self.env.company
            receivable_account = company.account_default_recv_account_id
            payable_account = company.account_default_pay_account_id
            
            # إذا لم تكن الحسابات معينة، نبحث عنها
            if not receivable_account:
                receivable_account = self.env['account.account'].search([
                    ('internal_type', '=', 'receivable'),
                    ('company_id', '=', company.id)
                ], limit=1)
                
            if not payable_account:
                payable_account = self.env['account.account'].search([
                    ('internal_type', '=', 'payable'),
                    ('company_id', '=', company.id)
                ], limit=1)
            
            # التحقق من وجود الحسابات
            if not receivable_account or not payable_account:
                raise UserError(_("لم يتم العثور على الحسابات الأساسية (مدينين/دائنين)"))
            
            domain = [
                ('partner_id', '=', self.customer_id.id),
                ('date', '<', self.date_from),
                ('account_id', 'in', [receivable_account.id, payable_account.id]),
                ('parent_state', '=', 'posted')
            ]
            
            if self.branch_id:
                domain.append(('branch_id', '=', self.branch_id.id))
                
            lines = self.env['account.move.line'].search(domain)
            return sum(lines.mapped('balance'))
            
        except UserError:
            raise
        except Exception as e:
            _logger.error("Error computing opening balance: %s", str(e))
            return 0.0
            

    def _get_transactions(self):
        """ جلب جميع الحركات المالية بشكل آمن """
        try:
            company = self.env.company
            receivable_account = company.account_default_recv_account_id
            payable_account = company.account_default_pay_account_id
            
            # البحث اليدوي إذا لم تكن الحسابات معينة
            if not receivable_account:
                receivable_account = self.env['account.account'].search([
                    ('internal_type', '=', 'receivable'),
                    ('company_id', '=', company.id)
                ], limit=1)
                
            if not payable_account:
                payable_account = self.env['account.account'].search([
                    ('internal_type', '=', 'payable'),
                    ('company_id', '=', company.id)
                ], limit=1)
            
            if not receivable_account or not payable_account:
                raise UserError(_("الحسابات الأساسية غير معينة (مدينين/دائنين)"))
            
            domain = [
                ('partner_id', '=', self.customer_id.id),
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
                ('account_id', 'in', [receivable_account.id, payable_account.id]),
                ('parent_state', '=', 'posted')
            ]
            
            if self.branch_id:
                domain.append(('branch_id', '=', self.branch_id.id))
                
            if self.payment_status == 'paid':
                domain.append(('full_reconcile_id', '!=', False))
            elif self.payment_status == 'not_paid':
                domain.append(('full_reconcile_id', '=', False))
            
            lines = self.env['account.move.line'].search(domain, order='date, id asc')
            
            transactions = []
            opening_balance = self._compute_opening_balance()
            balance = opening_balance
            
            for line in lines:
                try:
                    balance += line.debit - line.credit
                    transactions.append({
                        'date': line.date,
                        'move_type': self._get_move_type(line),
                        'name': line.name or line.move_id.name,
                        'reference': line.move_id.name,
                        'debit': line.debit,
                        'credit': line.credit,
                        'balance': balance,
                        'payment_status': 'مسددة' if line.full_reconcile_id else 'غير مسددة',
                        'journal': line.journal_id.name,
                        'currency': line.currency_id.name or line.company_id.currency_id.name,
                        'amount_currency': line.amount_currency if line.currency_id else line.balance
                    })
                except Exception as e:
                    _logger.warning("خطأ في معالجة بند القيد %s: %s", line.id, str(e))
                    continue
                    
            return transactions
            
        except UserError:
            raise
        except Exception as e:
            _logger.exception("فشل غير متوقع في جلب الحركات")
            raise UserError(_("حدث خطأ في جلب البيانات. يرجى مراجعة سجلات النظام."))
        
        
            
    def _get_move_type(self, line):
        """ تحديد نوع الحركة مع التعامل مع كافة الأنواع """
        move_type_map = {
            'out_invoice': 'فاتورة بيع',
            'out_refund': 'إشعار دائن',
            'out_receipt': 'إيصال بيع',
            'in_invoice': 'فاتورة شراء',
            'in_refund': 'إشعار مدين',
            'in_receipt': 'إيصال شراء',
            'entry': 'قيد محاسبي',
            'out_debit': 'مدين صادر',
            'in_debit': 'مدين وارد'
        }
        return move_type_map.get(line.move_id.move_type, 'حركة غير معروفة')
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
