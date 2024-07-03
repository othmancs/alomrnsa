from odoo import models
from datetime import date


class BranchComparison(models.AbstractModel):
    _name = 'report.sb_sale_edit_and_reports.report_branch_sales_comparison'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        for obj in partners:
            worksheet = workbook.add_worksheet('Sales Report')
            worksheet.right_to_left()
            row = 0
            col = 0
            worksheet.set_column(0, 8, 30)
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

            domain = [('date', '>=', obj.date_start),
                      ('date', '<=', obj.date_end),
                      ('state', '=', 'posted')
                      ]
            lines_data = self.env['account.move'].search(domain)

            product_category_id = obj.product_category_id.id
            line_data = lines_data.filtered(
                lambda x: any(line.product_id.categ_id.id == product_category_id for line in x.line_ids))
            existing_branch = line_data.mapped('branch_id')
            worksheet.merge_range(row, col + 3, row, col + 4, line_data.company_id.name, format4)
            worksheet.merge_range(row + 1, col + 3, row + 1, col + 4, 'مقارنة مبيعات الفروع ', format4)
            worksheet.merge_range(row + 5, col + 3, row + 5, col + 4, "فئه المنتج", format4)
            worksheet.merge_range(row + 6, col + 3, row + 6, col + 4, obj.product_category_id.name, format4)
            worksheet.write(row + 3, col + 5, ' :من ', format1)
            worksheet.write(row + 3, col + 7, '  :الى ', format1)
            worksheet.write(row + 3, col + 6, obj.date_start.strftime('%d/%m/%Y'), format3)
            worksheet.write(row + 3, col + 8, obj.date_end.strftime('%d/%m/%Y'), format3)
            worksheet.write(row + 3, col, ' :تاريخ طباعه ', format1)
            worksheet.write(row + 3, col + 1, date.today().strftime('%d/%m/%Y'), format3)
            worksheet.write(row + 4, col, ' :طبع من مستخدم  ', format1)
            worksheet.write(row + 4, col + 1, self.env.user.name, format3)

            row += 8
            worksheet.write(row, col, 'الفرع  ', format1)
            worksheet.write(row, col + 1, 'مبيعات نقدية   ', format1)
            worksheet.write(row, col + 2, 'مبيعات  أجلة   ', format1)
            worksheet.write(row, col + 3, 'اجمالى المبيعات   ', format1)
            worksheet.write(row, col + 4, 'الارجعات  ', format1)
            worksheet.write(row, col + 5, 'صافى المبيعات  ', format1)
            worksheet.write(row, col + 6, 'صافى التكلفة   ', format1)
            worksheet.write(row, col + 7, 'الربح', format1)
            worksheet.write(row, col + 8, 'التحصيل', format1)
            row += 1
            for branch in existing_branch:
                current_branch_lines = line_data.filtered(lambda x: x.branch_id == branch)
                total_option1_branch = sum([sum(move.line_ids.mapped('price_total')) for move in
                                                   current_branch_lines.filtered(
                                                    lambda x: x.move_type != 'out_refund' and x.payment_method == 'option1')])
                total_option2_branch = sum([sum(move.line_ids.mapped('price_total')) for move in
                                                   current_branch_lines.filtered(
                                                    lambda x: x.move_type != 'out_refund' and x.payment_method == 'option2')])
                total_op1_op2 = total_option1_branch + total_option2_branch
                out_refund_price = self.env['account.move'].search([
                    ('move_type', '=', 'out_refund'),
                    ('branch_id', '=', branch.id),
                    ('state', '=', 'posted')
                ])
                total_out_refund_price = sum(out_refund_price.mapped('amount_untaxed'))
                total_out_refund_purchase_price = sum(out_refund_price.line_ids.mapped('purchase_price'))

                total_all = abs(total_op1_op2-total_out_refund_price)
                profit = abs(total_all-total_out_refund_purchase_price)
                total_payments_branch = 0.0
                for line in current_branch_lines:
                    payments = self.env['account.payment'].search([
                        ('ref', '=', line.name),
                        ('state', '=', 'posted')
                    ])
                    total_payments_branch += sum(payments.mapped('amount_company_currency_signed'))
                worksheet.write(row, col, branch.name, format2)
                worksheet.write(row, col+1, total_option1_branch, format2)
                worksheet.write(row, col+2, total_option2_branch, format2)
                worksheet.write(row, col+3, total_op1_op2, format2)
                worksheet.write(row, col+4, total_out_refund_price, format2)
                worksheet.write(row, col+5, total_all, format2)
                worksheet.write(row, col+6, total_out_refund_purchase_price, format2)
                worksheet.write(row, col+7, profit, format2)
                worksheet.write(row, col + 8, total_payments_branch, format2)
                row += 1
