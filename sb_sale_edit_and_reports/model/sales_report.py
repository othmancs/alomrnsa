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
            worksheet.set_column(0, 10, 30)
            format1 = workbook.add_format(
                {'text_wrap': True, 'font_size': 11, 'align': 'center', 'bold': True,
                 'border': 1, 'bg_color': '#CCC7BF'})
            format2 = workbook.add_format(
                {'text_wrap': True, 'font_size': 11, 'align': 'center', 'bold': False,
                 'border': 1})
            format3 = workbook.add_format(
                {'text_wrap': True, 'font_size': 10,
                 'border': 1, 'bold': False, 'align': 'center'})
            format4 = workbook.add_format(
                {'text_wrap': True, 'font_size': 12, 'align': 'center', 'bold': True})
            format5 = workbook.add_format(
                {'text_wrap': True, 'font_size': 12, 'align': 'center', 'bold': True, 'bg_color': '#caf0f8'})
            domain = [('date', '>=', obj.date_start),
                      ('date', '<=', obj.date_end)]
            if obj.branch_ids:
                domain.append(('branch_id', 'in', obj.branch_ids.ids))
            lines_data = self.env['account.move'].search(domain)
            existing_branches = lines_data.mapped('branch_id')
            worksheet.merge_range(row, col + 3, row, col + 4, lines_data.company_id.name, format4)
            worksheet.merge_range(row + 1, col + 3, row + 1, col + 4, 'تقرير المبيعات', format4)
            worksheet.write(row + 3, col+5, ' :من ', format1)
            worksheet.write(row + 3, col + 7, '  :الى ', format1)
            worksheet.write(row + 3, col + 6, obj.date_start.strftime('%d/%m/%Y'), format3)
            worksheet.write(row + 3, col + 8,  obj.date_end.strftime('%d/%m/%Y'), format3)
            worksheet.write(row + 3, col, ' :تاريخ طباعه ', format1)
            worksheet.write(row + 3, col + 1, date.today().strftime('%d/%m/%Y'), format3)
            worksheet.write(row + 4, col, ' :طبع من مستخدم  ', format1)
            worksheet.write(row + 4, col + 1, self.env.user.name, format3)

            row += 8
            for branch in existing_branches:
                current_branch_lines = lines_data.filtered(lambda x: x.branch_id == branch)
                total_price_branch = sum([sum(move.line_ids.mapped('price_total')) for move in current_branch_lines.filtered(lambda x: x.move_type != 'out_refund')])
                total_out_refund_branch =sum([sum(move.line_ids.mapped('price_total')) for move in current_branch_lines.filtered(lambda x: x.move_type == 'out_refund')])
                total_out_refund_price_branch = sum([sum(move.line_ids.mapped('purchase_price')) for move in current_branch_lines.filtered(lambda x: x.move_type == 'out_refund')])
                print(total_out_refund_price_branch)
                total_out_refund_gty_branch = sum([sum(move.line_ids.mapped('quantity')) for move in current_branch_lines.filtered(lambda x: x.move_type == 'out_refund')])
                print(total_out_refund_gty_branch)
                total = total_out_refund_gty_branch*total_out_refund_price_branch
                total_discount_branch =sum([sum(move.line_ids.mapped('discount')) for move in current_branch_lines.filtered(lambda x: x.move_type != 'out_refund')])
                print(total_discount_branch)
                total_net_cost_branch = total_price_branch - total_discount_branch
                total_cost=sum([sum(move.line_ids.mapped('purchase_price')) for move in current_branch_lines.filtered(lambda x: x.move_type != 'out_refund')])

                worksheet.write(row, col + 9, total_out_refund_branch, format5)
                worksheet.write(row, col + 10, total, format5)
                worksheet.write(row, col, branch.name, format5)
                worksheet.merge_range(row, col + 1, row, col + 4, '', format5)
                worksheet.write(row, col + 5, total_price_branch, format5)
                worksheet.write(row, col + 6, total_discount_branch, format5)
                worksheet.write(row, col + 7, total_net_cost_branch, format5)
                worksheet.write(row, col + 8, total_cost, format5)
                row += 1
                worksheet.write(row, col, 'رقم الفاتورة ', format1)
                worksheet.write(row, col + 1, 'اسم البائع ', format1)
                worksheet.write(row, col + 2, 'اسم العميل ', format1)
                worksheet.write(row, col + 3, 'طريقة الدفع  ', format1)
                worksheet.write(row, col + 4, 'التاريخ  ', format1)
                worksheet.write(row, col + 5, 'اجمالى البيع    ', format1)
                worksheet.write(row, col + 6, 'خصم بيع   ', format1)
                worksheet.write(row, col + 7, 'صافى البيع  ', format1)
                worksheet.write(row, col + 8, 'اجمالى تكلفه البيع  ', format1)
                worksheet.write(row, col + 9, 'اجمالى الارجعات  ', format1)
                worksheet.write(row, col + 10, 'تكلفة الارجعات  ', format1)
                row += 1
                for account in current_branch_lines:
                    invoice_number = account.name
                    seller_name = account.created_by_id.name
                    customer_name = account.partner_id.name
                    invoice_date = account.invoice_date
                    cost =sum(account.line_ids.mapped('purchase_price'))
                    payment_method = account.payment_method
                    if account.move_type != 'out_refund':
                        total_price = sum(account.line_ids.mapped('price_total'))
                    else:
                        total_price = 0
                    total_discount = sum(account.line_ids.mapped('discount'))
                    net_cost = total_price-total_discount
                    worksheet.write(row, col, invoice_number, format2)
                    if seller_name:
                        worksheet.write(row, col+1, seller_name, format2)
                    else:
                        worksheet.write(row, col + 1, '-', format2)
                    worksheet.write(row, col+2, customer_name, format2)
                    if payment_method == 'option1':
                        worksheet.write(row, col+3, 'نقدى', format2)
                    elif payment_method == 'option2':
                        worksheet.write(row, col + 3, 'اجل', format2)
                    else:
                        worksheet.write(row, col + 3, '-', format2)
                    worksheet.write(row, col+4, format_date(self.env, invoice_date), format2)
                    worksheet.write(row, col+5, total_price, format2)
                    worksheet.write(row, col+6, total_discount, format2)
                    worksheet.write(row, col+7, net_cost, format2)
                    worksheet.write(row, col + 8, cost, format2)

                    if account.move_type == 'out_refund':
                        t = sum(account.line_ids.mapped('purchase_price'))*sum(account.line_ids.mapped('quantity'))
                        total_credit_note =sum(account.line_ids.mapped('price_total'))

                        worksheet.write(row, col + 9, total_credit_note, format2)
                        worksheet.write(row, col + 10, t, format2)
                    else:
                        worksheet.write(row, col + 9, 0, format2)
                        worksheet.write(row, col + 10, 0, format2)

                    row += 1
