from odoo import models
from datetime import date
from odoo.tools import format_date

class SalesReportReport(models.AbstractModel):
    _name = 'report.sb_sale_edit_and_reports.report_sales_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        for obj in partners:
            worksheet = workbook.add_worksheet('Sales Report')
            worksheet.right_to_left()
            row = 0
            col = 0
            
            # تعديل حجم الأعمدة
            worksheet.set_column(0, 0, 20)
            worksheet.set_column(1, 1, 30)
            worksheet.set_column(2, 2, 20)
            worksheet.set_column(3, 3, 15)
            worksheet.set_column(4, 4, 12)
            worksheet.set_column(5, 5, 12)
            worksheet.set_column(6, 6, 12)
            worksheet.set_column(7, 7, 12)

            # إنشاء التنسيقات
            format1 = workbook.add_format({
                'text_wrap': False, 'font_size': 11, 'align': 'center',
                'bold': True, 'border': 1, 'bg_color': '#CCC7BF'
            })
            format2 = workbook.add_format({
                'text_wrap': False, 'font_size': 11, 'align': 'center',
                'border': 1
            })
            format3 = workbook.add_format({
                'text_wrap': False, 'font_size': 10, 'border': 1,
                'align': 'center'
            })
            format4 = workbook.add_format({
                'text_wrap': False, 'font_size': 12, 'align': 'center',
                'bold': True
            })
            format5 = workbook.add_format({
                'text_wrap': False, 'font_size': 12, 'align': 'center',
                'bold': True, 'bg_color': '#caf0f8'
            })
            format6 = workbook.add_format({
                'text_wrap': False, 'font_size': 12, 'align': 'center',
                'bold': True, 'bg_color': 'red', 'color': 'white'
            })
            format7 = workbook.add_format({
                'text_wrap': False, 'font_size': 12, 'align': 'center',
                'bold': True, 'bg_color': 'green', 'color': 'white'
            })

            # تحديد شروط البحث
            domain = [
                ('invoice_date', '>=', obj.date_start),
                ('invoice_date', '<=', obj.date_end),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted')
            ]
            
            # فلترة حسب الفروع إذا تم تحديدها
            if obj.branch_ids:
                domain.append(('branch_id', 'in', obj.branch_ids.ids))
            
            # فلترة حسب نوع الدفع إذا لم يكن "الكل"
            if obj.payment_type and obj.payment_type != 'all':
                if obj.payment_type == 'cash':
                    domain.append(('payment_method', '=', 'option1'))
                elif obj.payment_type == 'credit':
                    domain.append(('payment_method', '=', 'option2'))

            lines_data = self.env['account.move'].search(domain)
            existing_branches = lines_data.mapped('branch_id')
            
            # إضافة عنوان التقرير
            payment_type_title = {
                'all': 'الكل',
                'cash': 'نقدي',
                'credit': 'آجل'
            }.get(obj.payment_type, 'الكل')
            
            worksheet.merge_range(row, col + 3, row, col + 4, lines_data.company_id.name, format4)
            worksheet.merge_range(row + 1, col + 3, row + 1, col + 4, 'تقرير المبيعات', format4)
            worksheet.write(row + 2, col + 3, f'نوع الدفع: {payment_type_title}', format4)
            
            # معلومات التاريخ والمستخدم
            worksheet.write(row + 3, col + 5, ' :من ', format1)
            worksheet.write(row + 3, col + 7, '  :الى ', format1)
            worksheet.write(row + 3, col + 6, format_date(self.env, obj.date_start), format3)
            worksheet.write(row + 3, col + 8, format_date(self.env, obj.date_end), format3)
            worksheet.write(row + 3, col, ' :تاريخ طباعه ', format1)
            worksheet.write(row + 3, col + 1, date.today().strftime('%d/%m/%Y'), format3)
            worksheet.write(row + 4, col, ' :طبع من مستخدم  ', format1)
            worksheet.write(row + 4, col + 1, self.env.user.name, format3)

            row += 8
            totals_by_payment_state = {'paid': 0, 'not_paid': 0, 'reversed': 0}

            for branch in existing_branches:
                current_branch_lines = lines_data.filtered(lambda x: x.branch_id == branch)
                unit_price_branch = sum([
                    sum(move.mapped('amount_untaxed'))
                    for move in current_branch_lines.filtered(lambda x: x.move_type != 'out_refund')
                ])
                
                worksheet.write(row, col, branch.name, format5)
                worksheet.merge_range(row, col + 1, row, col + 4, '', format5)
                worksheet.write(row, col + 5, unit_price_branch, format5)

                total_out_refund_purchase_price = 0.0
                for line in current_branch_lines:
                    out_refund_price = self.env['account.move'].search([
                        ('move_type', '=', 'out_refund'),
                        ('branch_id', '=', branch.id),
                        ('reversed_entry_id', '=', line.id),
                        ('state', '=', 'posted')
                    ])
                    total_out_refund_purchase_price += sum(
                        out_refund_price.line_ids.mapped(lambda x: x.purchase_price * x.quantity)
                    )
                worksheet.write(row, col + 6, total_out_refund_purchase_price, format5)
                row += 1

                # كتابة العناوين
                worksheet.write(row, col, 'رقم الفاتورة ', format1)
                worksheet.write(row, col + 1, 'اسم البائع ', format1)
                worksheet.write(row, col + 2, 'اسم العميل ', format1)
                worksheet.write(row, col + 3, 'طريقة الدفع  ', format1)
                worksheet.write(row, col + 4, 'التاريخ  ', format1)
                worksheet.write(row, col + 5, 'صافى البيع ق ', format1)
                worksheet.write(row, col + 6, 'صافي الارجاعات ق ', format1)
                worksheet.write(row, col + 7, ' حاله الدفع ', format1)
                row += 1

                for account in current_branch_lines:
                    invoice_number = account.name
                    seller_name = account.created_by_id.name
                    customer_name = account.partner_id.name
                    invoice_date = account.invoice_date
                    state = account.payment_state
                    payment_method = account.payment_method

                    # معالجة حالة 'reversed' وإضافتها للإجماليات
                    if state not in totals_by_payment_state:
                        state = 'reversed'
                    totals_by_payment_state[state] += sum(account.mapped('amount_untaxed'))
                    
                    net_cost = sum(
                        account.line_ids.mapped(lambda line: (line.price_unit * line.quantity) - line.discount)
                    )

                    # تحديد تنسيق حالة الدفع
                    payment_status = {
                        'paid': ('مدفوع', format7),
                        'not_paid': ('غير مدفوع', format6),
                        'reversed': ('معكوس', format6)
                    }.get(state, ('غير محدد', format2))
                    
                    worksheet.write(row, col + 7, payment_status[0], payment_status[1])

                    worksheet.write(row, col, invoice_number, format2)
                    worksheet.write(row, col + 1, seller_name, format2)
                    worksheet.write(row, col + 2, customer_name, format2)
                    
                    # عرض طريقة الدفع
                    payment_display = {
                        'option1': 'نقدى',
                        'option2': 'اجل'
                    }.get(payment_method, '-')
                    worksheet.write(row, col + 3, payment_display, format2)
                    
                    worksheet.write(row, col + 4, format_date(self.env, invoice_date), format2)
                    worksheet.write(row, col + 5, net_cost, format2)

                    out_refund = self.env['account.move'].search([
                        ('move_type', '=', 'out_refund'),
                        ('branch_id', '=', branch.id),
                        ('reversed_entry_id', '=', account.id),
                        ('state', '=', 'posted')
                    ])
                    out_refund_purchase_price = sum(
                        out_refund.line_ids.mapped(lambda x: x.purchase_price * x.quantity)
                    )
                    worksheet.write(row, col + 6, out_refund_purchase_price, format2)
                    row += 1

            # إضافة الإجماليات لكل طريقة دفع
            row += 2
            worksheet.write(row, col, 'إجماليات حسب حالة الدفع', format5)
            row += 1
            
            # عرض الإجماليات لكل الحالات الممكنة
            payment_statuses = [
                ('paid', 'نقدي (مدفوع)'),
                ('not_paid', 'آجل (غير مدفوع)'),
                ('reversed', 'معكوس')
            ]
            
            for status, label in payment_statuses:
                if totals_by_payment_state.get(status, 0) != 0:
                    worksheet.write(row, col, label, format2)
                    worksheet.write(row, col + 1, totals_by_payment_state.get(status, 0), format2)
                    row += 1
            
            # الإجمالي الكلي
            total_all = sum(totals_by_payment_state.values())
            worksheet.write(row, col, 'الإجمالي الكلي', format5)
            worksheet.write(row, col + 1, total_all, format5)
