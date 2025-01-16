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
            format1 = workbook.add_format({'text_wrap': True, 'font_size': 11, 'align': 'center', 'bold': True, 'border': 1, 'bg_color': '#CCC7BF'})
            format2 = workbook.add_format({'text_wrap': True, 'font_size': 11, 'align': 'center', 'bold': False, 'border': 1})
            format3 = workbook.add_format({'text_wrap': True, 'font_size': 10, 'border': 1, 'bold': False, 'align': 'center'})
            format4 = workbook.add_format({'text_wrap': True, 'font_size': 12, 'align': 'center', 'bold': True})
            format5 = workbook.add_format({'text_wrap': True, 'font_size': 12, 'align': 'center', 'bold': True, 'bg_color': '#caf0f8'})
            format6 = workbook.add_format({'text_wrap': True, 'font_size': 12, 'align': 'center', 'bold': True, 'bg_color': 'red', 'color': 'white'})
            format7 = workbook.add_format({'text_wrap': True, 'font_size': 12, 'align': 'center', 'bold': True, 'bg_color': 'green', 'color': 'white'})

            domain = [('invoice_date', '>=', obj.date_start),
                      ('invoice_date', '<=', obj.date_end),
                      ('move_type', '=', 'out_invoice'),
                      ('state', '=', 'posted')]

            if obj.payment_method:
                domain.append(('payment_method', '=', obj.payment_method.id))

            if obj.branch_ids:
                domain.append(('branch_id', 'in', obj.branch_ids.ids))

            lines_data = self.env['account.move'].search(domain)
            existing_branches = lines_data.mapped('branch_id')
            worksheet.merge_range(row, col + 3, row, col + 4, lines_data.company_id.name, format4)
            worksheet.merge_range(row + 1, col + 3, row + 1, col + 4, 'تقرير المبيعات', format4)
            worksheet.write(row + 3, col + 5, ' :من ', format1)
            worksheet.write(row + 3, col + 7, '  :الى ', format1)
            worksheet.write(row + 3, col + 6, obj.date_start.strftime('%d/%m/%Y'), format3)
            worksheet.write(row + 3, col + 8,  obj.date_end.strftime('%d/%m/%Y'), format3)
            worksheet.write(row + 3, col, ' :تاريخ طباعه ', format1)
            worksheet.write(row + 3, col + 1, date.today().strftime('%d/%m/%Y'), format3)
            worksheet.write(row + 4, col, ' :طبع من مستخدم  ', format1)
            worksheet.write(row + 4, col + 1, self.env.user.name, format3)

            row += 8

            totals_by_payment_method = {}

            for branch in existing_branches:
                current_branch_lines = lines_data.filtered(lambda x: x.branch_id == branch)
                unit_price_branch = sum([sum(move.mapped('amount_untaxed')) for move in current_branch_lines.filtered(lambda x: x.move_type != 'out_refund')])
                total_discount_branch = sum([sum(move.line_ids.mapped('discount')) for move in current_branch_lines.filtered(lambda x: x.move_type != 'out_refund')])
                branch_amount_untaxed = sum([sum(move.line_ids.mapped(lambda line: (line.price_unit * line.quantity) - line.discount)) for move in current_branch_lines.filtered(lambda x: x.move_type != 'out_refund')])

                worksheet.write(row, col, branch.name, format5)
                worksheet.merge_range(row, col + 1, row, col + 4, '', format5)
                worksheet.write(row, col + 5, unit_price_branch, format5)
                worksheet.write(row, col + 6, total_discount_branch, format5)
                worksheet.write(row, col + 7, branch_amount_untaxed, format5)
                row += 1
                worksheet.write(row, col, 'رقم الفاتورة ', format1)
                worksheet.write(row, col + 1, 'اسم البائع ', format1)
                worksheet.write(row, col + 2, 'اسم العميل ', format1)
                worksheet.write(row, col + 3, 'طريقة الدفع  ', format1)
                worksheet.write(row, col + 4, 'التاريخ  ', format1)
                worksheet.write(row, col + 5, 'اجمالى البيع    ', format1)
                worksheet.write(row, col + 6, 'خصم بيع   ', format1)
                worksheet.write(row, col + 7, 'صافى البيع  ', format1)
                worksheet.write(row, col + 8, ' حاله الدفع ', format1)
                row += 1

                for account in current_branch_lines:
                    invoice_number = account.name
                    seller_name = account.created_by_id.name
                    customer_name = account.partner_id.name
                    invoice_date = account.invoice_date
                    state = account.payment_state
                    payment_method = account.payment_method

                    if payment_method not in totals_by_payment_method:
                        totals_by_payment_method[payment_method] = 0

                    totals_by_payment_method[payment_method] += sum(account.mapped('amount_untaxed'))

                    if state == 'paid':
                        worksheet.write(row, col + 8, 'مدفوع', format7)
                    elif state == 'not_paid':
                        worksheet.write(row, col + 8, 'غير مدفوع', format6)

                    price = sum(account.mapped('amount_untaxed'))
                    total_discount = sum(account.line_ids.mapped('discount'))
                    net_cost = sum(account.line_ids.mapped(lambda line: (line.price_unit * line.quantity) - line.discount))

                    worksheet.write(row, col, invoice_number, format2)
                    worksheet.write(row, col + 1, seller_name, format2)
                    worksheet.write(row, col + 2, customer_name, format2)
                    # worksheet.write(row, col + 3, payment_method or '-', format2)
                     if payment_method == 'option1':
                            worksheet.write(row, col + 3, 'نقدى', format2)
                        elif payment_method == 'option2':
                            worksheet.write(row, col + 3, 'اجل', format2)
                        else:
                            worksheet.write(row, col + 3, '-', format2)
                    worksheet.write(row, col + 4, format_date(self.env, invoice_date), format2)
                    worksheet.write(row, col + 5, price, format2)
                    worksheet.write(row, col + 6, total_discount, format2)
                    worksheet.write(row, col + 7, net_cost, format2)

                    row += 1

            # إضافة الإجماليات لكل طريقة دفع
            row += 2
            worksheet.write(row, col, 'إجماليات حسب طريقة الدفع', format5)
            row += 1

            for payment_method, total in totals_by_payment_method.items():
                worksheet.write(row, col, payment_method or 'غير محدد', format2)
                worksheet.write(row, col + 1, total, format2)
                row += 1

# from odoo import models
# from datetime import date
# from odoo.tools import format_date



# class SalesReportReport(models.AbstractModel):
#     _name = 'report.sb_sale_edit_and_reports.report_sales_report'
#     _inherit = 'report.report_xlsx.abstract'

#     def generate_xlsx_report(self, workbook, data, partners):
#         for obj in partners:
#             worksheet = workbook.add_worksheet('Sales Report')
#             worksheet.right_to_left()
#             row = 0
#             col = 0
#             worksheet.set_column(0, 10, 30)
#             format1 = workbook.add_format({'text_wrap': True, 'font_size': 11, 'align': 'center', 'bold': True, 'border': 1, 'bg_color': '#CCC7BF'})
#             format2 = workbook.add_format({'text_wrap': True, 'font_size': 11, 'align': 'center', 'bold': False, 'border': 1})
#             format3 = workbook.add_format({'text_wrap': True, 'font_size': 10, 'border': 1, 'bold': False, 'align': 'center'})
#             format4 = workbook.add_format({'text_wrap': True, 'font_size': 12, 'align': 'center', 'bold': True})
#             format5 = workbook.add_format({'text_wrap': True, 'font_size': 12, 'align': 'center', 'bold': True, 'bg_color': '#caf0f8'})
#             format6 = workbook.add_format({'text_wrap': True, 'font_size': 12, 'align': 'center', 'bold': True, 'bg_color': 'red', 'color': 'white'})
#             format7 = workbook.add_format({'text_wrap': True, 'font_size': 12, 'align': 'center', 'bold': True, 'bg_color': 'green', 'color': 'white'})

#             domain = [('invoice_date', '>=', obj.date_start),
#                       ('invoice_date', '<=', obj.date_end),
#                       ('move_type', '=', 'out_invoice'),
#                       ('state', '=', 'posted')]

#             # تصفية طريقة الدفع
#             if obj.payment_method:
#                 domain.append(('payment_method', '=', obj.payment_method.id))

#             if obj.branch_ids:
#                 domain.append(('branch_id', 'in', obj.branch_ids.ids))

#             lines_data = self.env['account.move'].search(domain)
#             existing_branches = lines_data.mapped('branch_id')
#             worksheet.merge_range(row, col + 3, row, col + 4, lines_data.company_id.name, format4)
#             worksheet.merge_range(row + 1, col + 3, row + 1, col + 4, 'تقرير المبيعات', format4)
#             worksheet.write(row + 3, col + 5, ' :من ', format1)
#             worksheet.write(row + 3, col + 7, '  :الى ', format1)
#             worksheet.write(row + 3, col + 6, obj.date_start.strftime('%d/%m/%Y'), format3)
#             worksheet.write(row + 3, col + 8,  obj.date_end.strftime('%d/%m/%Y'), format3)
#             worksheet.write(row + 3, col, ' :تاريخ طباعه ', format1)
#             worksheet.write(row + 3, col + 1, date.today().strftime('%d/%m/%Y'), format3)
#             worksheet.write(row + 4, col, ' :طبع من مستخدم  ', format1)
#             worksheet.write(row + 4, col + 1, self.env.user.name, format3)

#             row += 8

#             for branch in existing_branches:
#                 current_branch_lines = lines_data.filtered(lambda x: x.branch_id == branch)
#                 unit_price_branch = sum([sum(move.mapped('amount_untaxed')) for move in current_branch_lines.filtered(lambda x: x.move_type != 'out_refund')])
#                 total_discount_branch = sum([sum(move.line_ids.mapped('discount')) for move in current_branch_lines.filtered(lambda x: x.move_type != 'out_refund')])
#                 branch_amount_untaxed = sum([sum(move.line_ids.mapped(lambda line: (line.price_unit * line.quantity) - line.discount)) for move in current_branch_lines.filtered(lambda x: x.move_type != 'out_refund')])
#                 total_cost_branch = sum([sum(move.line_ids.mapped(lambda line: line.purchase_price * line.quantity)) for move in current_branch_lines.filtered(lambda x: x.move_type != 'out_refund')])

#                 total_out_refund_purchase_price = 0.0
#                 total_out_refund_price = 0.0
#                 for line in current_branch_lines:
#                     out_refund_price = self.env['account.move'].search([
#                         ('move_type', '=', 'out_refund'),
#                         ('branch_id', '=', branch.id),
#                         ('reversed_entry_id', '=', line.id),
#                         ('state', '=', 'posted')
#                     ])
#                     total_out_refund_price += sum(out_refund_price.line_ids.mapped(lambda x: x.price_unit * x.quantity))
#                     total_out_refund_purchase_price += sum(out_refund_price.line_ids.mapped(lambda x: x.purchase_price * x.quantity))
#                     worksheet.write(row, col + 9, total_out_refund_price, format5)
#                     worksheet.write(row, col + 10, total_out_refund_purchase_price, format5)

#                 worksheet.write(row, col, branch.name, format5)
#                 worksheet.merge_range(row, col + 1, row, col + 4, '', format5)
#                 worksheet.write(row, col + 5, unit_price_branch, format5)
#                 worksheet.write(row, col + 6, total_discount_branch, format5)
#                 worksheet.write(row, col + 7, branch_amount_untaxed, format5)
#                 worksheet.write(row, col + 8, total_cost_branch, format5)
#                 row += 1
#                 worksheet.write(row, col, 'رقم الفاتورة ', format1)
#                 worksheet.write(row, col + 1, 'اسم البائع ', format1)
#                 worksheet.write(row, col + 2, 'اسم العميل ', format1)
#                 worksheet.write(row, col + 3, 'طريقة الدفع  ', format1)
#                 worksheet.write(row, col + 4, 'التاريخ  ', format1)
#                 worksheet.write(row, col + 5, 'اجمالى البيع    ', format1)
#                 worksheet.write(row, col + 6, 'خصم بيع   ', format1)
#                 worksheet.write(row, col + 7, 'صافى البيع  ', format1)
#                 worksheet.write(row, col + 8, 'اجمالى تكلفه البيع  ', format1)
#                 worksheet.write(row, col + 9, 'اجمالى الارجعات  ', format1)
#                 worksheet.write(row, col + 10, 'تكلفة الارجعات  ', format1)
#                 worksheet.write(row, col + 11, ' حاله الدفع ', format1)
#                 row += 1
#                 for account in current_branch_lines:
#                     invoice_number = account.name
#                     seller_name = account.created_by_id.name
#                     customer_name = account.partner_id.name
#                     invoice_date = account.invoice_date
#                     state = account.payment_state
#                     if state == 'paid':
#                         worksheet.write(row, col + 11, 'مدفوع', format7)
#                     elif state == 'not_paid':
#                         worksheet.write(row, col + 11, 'غير مدفوع', format6)

#                     cost = sum(account.line_ids.mapped(lambda line: line.purchase_price * line.quantity))
#                     payment_method = account.payment_method
#                     price = sum(account.mapped('amount_untaxed'))
#                     total_discount = sum(account.line_ids.mapped('discount'))
#                     net_cost = sum(account.line_ids.mapped(lambda line: (line.price_unit * line.quantity) - line.discount))
#                     worksheet.write(row, col, invoice_number, format2)
#                     worksheet.write(row, col + 1, seller_name, format2)
#                     worksheet.write(row, col + 2, customer_name, format2)

#                     # تحديد طريقة الدفع
#                     if payment_method == 'option1':
#                         worksheet.write(row, col + 3, 'نقدى', format2)
#                     elif payment_method == 'option2':
#                         worksheet.write(row, col + 3, 'اجل', format2)
#                     else:
#                         worksheet.write(row, col + 3, '-', format2)

#                     worksheet.write(row, col + 4, format_date(self.env, invoice_date), format2)
#                     worksheet.write(row, col + 5, price, format2)
#                     worksheet.write(row, col + 6, total_discount, format2)
#                     worksheet.write(row, col + 7, net_cost, format2)
#                     worksheet.write(row, col + 8, cost, format2)

#                     out_refund = self.env['account.move'].search([
#                         ('move_type', '=', 'out_refund'),
#                         ('branch_id', '=', branch.id),
#                         ('reversed_entry_id', '=', account.id),
#                         ('state', '=', 'posted')
#                     ])
#                     for ac in out_refund:
#                         out_refund_purchase_price = sum(ac.line_ids.mapped(lambda x: x.purchase_price * x.quantity))
#                         out_refund_price = sum(ac.mapped('amount_untaxed'))
#                         worksheet.write(row, col + 9, out_refund_price, format2)
#                         worksheet.write(row, col + 10, out_refund_purchase_price, format2)

#                     row += 1
