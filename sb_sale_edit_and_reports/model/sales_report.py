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
            # Column width adjustments
            worksheet.set_column(0, 0, 20)
            worksheet.set_column(1, 1, 30)
            worksheet.set_column(2, 2, 20)
            worksheet.set_column(3, 3, 15)
            worksheet.set_column(4, 4, 12)
            worksheet.set_column(5, 5, 12)
            worksheet.set_column(6, 6, 12)
            worksheet.set_column(7, 7, 12)

            # Create formats
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

            # Search domain
            domain = [
                ('invoice_date', '>=', obj.date_start),
                ('invoice_date', '<=', obj.date_end),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted')
            ]
            
            # Filter by branch if selected
            if obj.branch_ids:
                domain.append(('branch_id', 'in', obj.branch_ids.ids))
            
            # Filter by payment type if not 'all'
            if obj.payment_type and obj.payment_type != 'all':
                domain.append(('invoice_payment_term_id', '!=', False) if obj.payment_type == 'credit' else domain.append(('invoice_payment_term_id', '=', False))

            lines_data = self.env['account.move'].search(domain)
            existing_branches = lines_data.mapped('branch_id')
            
            # Add title showing selected payment type
            payment_type_title = {
                'all': 'الكل',
                'cash': 'نقدي',
                'credit': 'آجل'
            }.get(obj.payment_type, 'الكل')
            
            worksheet.merge_range(row, col + 3, row, col + 4, lines_data.company_id.name, format4)
            worksheet.merge_range(row + 1, col + 3, row + 1, col + 4, 'تقرير المبيعات', format4)
            worksheet.write(row + 2, col + 3, f'نوع الدفع: {payment_type_title}', format4)
            
            worksheet.write(row + 3, col + 5, ' :من ', format1)
            worksheet.write(row + 3, col + 7, '  :الى ', format1)
            worksheet.write(row + 3, col + 6, format_date(self.env, obj.date_start), format3)
            worksheet.write(row + 3, col + 8, format_date(self.env, obj.date_end), format3)
            worksheet.write(row + 3, col, ' :تاريخ طباعه ', format1)
            worksheet.write(row + 3, col + 1, date.today().strftime('%d/%m/%Y'), format3)
            worksheet.write(row + 4, col, ' :طبع من مستخدم  ', format1)
            worksheet.write(row + 4, col + 1, self.env.user.name, format3)

            row += 8
            totals_by_payment_type = {'cash': 0, 'credit': 0}

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

                # Write headers
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
                    is_credit = bool(account.invoice_payment_term_id)  # True for credit, False for cash

                    payment_type = 'credit' if is_credit else 'cash'
                    totals_by_payment_type[payment_type] += sum(account.mapped('amount_untaxed'))
                    
                    net_cost = sum(
                        account.line_ids.mapped(lambda line: (line.price_unit * line.quantity) - line.discount)
                    )

                    if state == 'paid':
                        worksheet.write(row, col + 7, 'مدفوع', format7)
                    elif state == 'not_paid':
                        worksheet.write(row, col + 7, 'غير مدفوع', format6)

                    worksheet.write(row, col, invoice_number, format2)
                    worksheet.write(row, col + 1, seller_name, format2)
                    worksheet.write(row, col + 2, customer_name, format2)
                    
                    # Display payment type
                    payment_display = 'اجل' if is_credit else 'نقدى'
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

            # Add totals by payment type
            row += 2
            worksheet.write(row, col, 'إجماليات حسب طريقة الدفع', format5)
            row += 1
            for payment_type, total in totals_by_payment_type.items():
                payment_label = 'اجل' if payment_type == 'credit' else 'نقدى'
                worksheet.write(row, col, payment_label, format2)
                worksheet.write(row, col + 1, total, format2)
                row += 1
