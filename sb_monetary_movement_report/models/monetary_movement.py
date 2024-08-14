from odoo import models
from datetime import date


class BranchComparison(models.AbstractModel):
    _name = 'report.sb_monetary_movement_report.report_monetary_movement'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):

        for obj in partners:
            worksheet = workbook.add_worksheet('Sales Report')
            worksheet.right_to_left()
            row = 0
            col = 0
            worksheet.set_column(0, 6, 30)
            format1 = workbook.add_format(
                {'text_wrap': True, 'font_size': 11, 'align': 'center', 'bold': True,
                 'border': 1, 'bg_color': '#CCC7BF'})
            format2 = workbook.add_format(
                {'text_wrap': True, 'font_size': 11, 'align': 'right', 'bold': False,
                 'border': 1,'bg_color':'#FFE4CF'})
            format3 = workbook.add_format(
                {'text_wrap': True, 'font_size': 10,
                 'border': 1, 'bold': False, 'align': 'center'})
            format4 = workbook.add_format(
                {'text_wrap': True, 'font_size': 12, 'align': 'center', 'bold': True})
            format5 = workbook.add_format(
                {'text_wrap': True, 'font_size': 11, 'align': 'center', 'bold': True,
                 'border': 1, 'bg_color': '#D0B8A8'})
            # worksheet.set_column(2, 2, 7)

            domain = [('invoice_date', '>=', obj.date_start),
                      ('invoice_date', '<=', obj.date_end),
                      ('state', '=', 'posted'),
                      ('move_type', '=', 'out_invoice'),
                      ('branch_id','=',obj.branch_id.ids)
                      ]
            lines_data = self.env['account.move'].search(domain)
            existing_branch = lines_data.mapped('branch_id')



            worksheet.merge_range(row + 1, col + 2, row + 1, col + 3, 'تقرير الحركه النقديه ', format4)
            worksheet.merge_range(row, col + 2, row, col + 3, lines_data.company_id.name, format4)
            # worksheet.merge_range(row + 5, col + 2, row + 5, col + 3, "الفرع", format4)
            # worksheet.merge_range(row + 6, col + 2, row + 6, col + 3, obj.branch_id.name, format4)
            worksheet.write(row + 3, col + 4, ' :من ', format1)
            worksheet.write(row + 4, col + 4, '  :الى ', format1)
            worksheet.write(row + 3, col + 5, obj.date_start.strftime('%d/%m/%Y'), format3)
            worksheet.write(row + 4, col + 5, obj.date_end.strftime('%d/%m/%Y'), format3)
            worksheet.write(row + 3, col, ' :تاريخ طباعه ', format1)
            worksheet.write(row + 3, col + 1, date.today().strftime('%d/%m/%Y'), format3)
            worksheet.write(row + 4, col, ' :طبع من مستخدم  ', format1)
            worksheet.write(row + 4, col + 1, self.env.user.name, format3)

            row += 8

            for branch in existing_branch:
                # worksheet.write(row, col + 4, branch.name, format1)
                worksheet.merge_range(row, col, row, col + 6, branch.name, format2)
                row += 1
                worksheet.write(row, col, '', format1)
                worksheet.write(row, col +1, 'اجمالى نقدى', format1)
                worksheet.write(row, col +2, 'اجمالى اجل', format1)
                worksheet.write(row, col +3, 'شبكه', format1)
                worksheet.write(row, col +4, 'فيزا', format1)
                worksheet.write(row, col +5, 'شيك', format1)
                worksheet.write(row, col +6, 'حواله بنكيه', format1)
                worksheet.write(row+1, col, 'مبيعات', format1)
                worksheet.write(row+2, col, 'ض.مبيعات', format1)
                worksheet.write(row+3, col, 'ارجاعات', format1)
                worksheet.write(row+4, col, 'ض.ارجاعات', format1)
                worksheet.write(row+5, col, 'مقبوضات', format1)
                worksheet.write(row+6, col, 'الاجمالى', format5)
                row+=1
                current_branch_lines = lines_data.filtered(lambda x: x.branch_id == branch)
                total_option1_branch = sum([sum(move.mapped('amount_untaxed')) for move in
                                            current_branch_lines.filtered(lambda x: x.payment_method == 'option1' and x.move_type != 'out_refund')])
                total_option2_branch = sum([sum(move.mapped('amount_untaxed')) for move in
                                            current_branch_lines.filtered(lambda x: x.payment_method == 'option2' and x.move_type != 'out_refund')])
                worksheet.write(row, col+1, total_option1_branch, format3)
                worksheet.write(row, col + 2, total_option2_branch, format3)
                worksheet.write(row, col + 3, '-', format3)
                worksheet.write(row, col + 4, '-', format3)
                worksheet.write(row, col + 5, '-', format3)
                worksheet.write(row, col + 6, '-', format3)
                row +=1
                total_option1_branch_tax = sum([sum(move.mapped('amount_tax_signed')) for move in
                                            current_branch_lines.filtered(lambda
                                                                              x: x.payment_method == 'option1' and x.move_type != 'out_refund')])
                total_option2_branch_tax = sum([sum(move.mapped('amount_tax_signed')) for move in
                                            current_branch_lines.filtered(lambda
                                                                              x: x.payment_method == 'option2' and x.move_type != 'out_refund')])
                worksheet.write(row, col + 1, total_option1_branch_tax, format3)
                worksheet.write(row, col + 2, total_option2_branch_tax, format3)
                worksheet.write(row, col + 3, '-', format3)
                worksheet.write(row, col + 4, '-', format3)
                worksheet.write(row, col + 5, '-', format3)
                worksheet.write(row, col + 6, '-', format3)
                row += 1

                out_refund = self.env['account.move'].search([
                    ('invoice_date', '>=', obj.date_start),
                    ('invoice_date', '<=', obj.date_end),
                    ('move_type', '=', 'out_refund'),
                    ('branch_id', '=', branch.id),
                    ('state', '=', 'posted')
                ])
                total_option1_out_refund = sum([sum(move.mapped('amount_untaxed')) for move in
                                            out_refund.filtered(lambda
                                                                              x: x.payment_method == 'option1' )])
                total_option2_out_refund = sum([sum(move.mapped('amount_untaxed')) for move in
                                            out_refund.filtered(lambda
                                                                              x: x.payment_method == 'option2' )])
                worksheet.write(row, col + 1, total_option1_out_refund, format3)
                worksheet.write(row, col + 2, total_option2_out_refund, format3)
                worksheet.write(row, col + 3, '-', format3)
                worksheet.write(row, col + 4, '-', format3)
                worksheet.write(row, col + 5, '-', format3)
                worksheet.write(row, col + 6, '-', format3)
                row+=1
                total_option1_tax_out_refund = abs(sum([sum(move.mapped('amount_tax_signed')) for move in
                                                out_refund.filtered(lambda
                                                                        x: x.payment_method == 'option1')]))
                total_option2_tax_out_refund = abs(sum([sum(move.mapped('amount_tax_signed')) for move in
                                                out_refund.filtered(lambda
                                                                        x: x.payment_method == 'option2')]))
                worksheet.write(row, col + 1, total_option1_tax_out_refund, format3)
                worksheet.write(row, col + 2, total_option2_tax_out_refund, format3)
                worksheet.write(row, col + 3, '-', format3)
                worksheet.write(row, col + 4, '-', format3)
                worksheet.write(row, col + 5, '-', format3)
                worksheet.write(row, col + 6, '-', format3)
                row += 1
                payments = self.env['account.payment'].search([
                    ('branch_id', '=', branch.id),
                    ('state', '=', 'posted'),
                    ('date', '>=', obj.date_start),
                    ('date', '<=', obj.date_end)
                ])
                total_payments_branch1 = sum(payment.amount_company_currency_signed for payment in payments if payment.payment_method_line_id.name == 'تحويل')
                total_payments_branch2 = sum(payment.amount_company_currency_signed for payment in payments if payment.payment_method_line_id.name == 'تحويل')
                total_payments_branch3 = sum(payment.amount_company_currency_signed for payment in payments if payment.payment_method_line_id.name == 'تحويل')
                total_payments_branch4 = sum(payment.amount_company_currency_signed for payment in payments if payment.payment_method_line_id.name == 'تحويل')
                worksheet.write(row, col + 1,'-' , format3)
                worksheet.write(row, col + 2, '-', format3)
                worksheet.write(row, col + 3, total_payments_branch1, format3)
                worksheet.write(row, col + 4, total_payments_branch2, format3)
                worksheet.write(row, col + 5, total_payments_branch3, format3)
                worksheet.write(row, col + 6, total_payments_branch4, format3)
                row += 1
                total1= abs(round(total_option1_branch + total_option1_branch_tax + total_option1_out_refund + total_option1_tax_out_refund,2))
                total2= abs(round(total_option2_branch + total_option2_branch_tax + total_option2_out_refund + total_option2_tax_out_refund,2))
                worksheet.write(row, col + 1, total1, format5)
                worksheet.write(row, col + 2, total2, format5)
                worksheet.write(row, col + 3, total_payments_branch1, format5)
                worksheet.write(row, col + 4, total_payments_branch2, format5)
                worksheet.write(row, col + 5, total_payments_branch3, format5)
                worksheet.write(row, col + 6, total_payments_branch4, format5)
                row += 1










