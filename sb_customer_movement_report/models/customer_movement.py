from odoo import models
from datetime import date


class BranchComparison(models.AbstractModel):
    _name = 'report.sb_customer_movement_report.report_customer_movement'
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
                {'text_wrap': True, 'font_size': 11, 'align': 'right', 'bold': True,
                 'border': 1, 'bg_color': '#FFE4CF'})
            format3 = workbook.add_format(
                {'text_wrap': True, 'font_size': 10,
                 'border': 1, 'bold': False, 'align': 'center'})
            format4 = workbook.add_format(
                {'text_wrap': True, 'font_size': 12, 'align': 'center', 'bold': True})
            format5 = workbook.add_format({
                'text_wrap': True,
                'font_size': 11,
                'align': 'center',
                'bold': True,
                'border': 1,
                'border_color': '#CCC7BF',
                'bg_color': '#CCC7BF',
                'top': 1,
                'top_color': 'black'
            })

            domain = [
                ('invoice_date', '>=', obj.date_start),
                ('invoice_date', '<=', obj.date_end),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                # ('partner_id', 'in', obj.partner_id.ids)
            ]
            if obj.partner_id.ids:
                domain.append(('partner_id', 'in', obj.partner_id.ids))
            lines_data = self.env['account.move'].search(domain)
            domain_new = [
                ('date', '<', obj.date_start)
            ]
            balance_data = self.env['account.move.line'].search(domain_new)
            payment_domain = [
                ('date', '>=', obj.date_start),
                ('date', '<=', obj.date_end),
                ('state', '=', 'posted')
            ]
            payment_data = self.env['account.payment'].search(payment_domain)

            worksheet.merge_range(row + 1, col + 2, row + 1, col + 3, 'تقرير حركه العملاء ', format4)
            worksheet.merge_range(row, col + 2, row, col + 3, lines_data.company_id.name, format4)
            worksheet.write(row + 3, col, ' :تاريخ طباعه ', format1)
            worksheet.write(row + 3, col + 1, date.today().strftime('%d/%m/%Y'), format3)
            worksheet.write(row + 4, col, ' :طبع من مستخدم  ', format1)
            worksheet.write(row + 4, col + 1, self.env.user.name, format3)

            row += 8
            processed_partner_ids = set()

            for branch in obj.branch_id:
                branch_lines_data = lines_data.filtered(lambda x: x.partner_id.branch_id == branch)

                print('eeeeeeeeeeeeeeeeeeeeeeeee',branch_lines_data)
                if branch_lines_data:
                    worksheet.merge_range(row, col, row, col + 8, branch.name, format2)
                    row += 1
                    worksheet.write(row, col + 3, "حركه العملاء من", format5)
                    worksheet.write(row, col + 4, obj.date_start.strftime('%d/%m/%Y'), format5)
                    worksheet.write(row, col + 5, "الى", format5)
                    worksheet.write(row, col + 6, obj.date_end.strftime('%d/%m/%Y'), format5)
                    row += 1
                    worksheet.write(row, col, 'رقم العميل', format1)
                    worksheet.write(row, col + 1, 'اسم العميل', format1)
                    worksheet.write(row, col + 2, 'رصيد اول المده', format1)
                    worksheet.write(row, col + 3, 'المبيعات', format1)
                    worksheet.write(row, col + 4, 'تسويه م', format1)
                    worksheet.write(row, col + 5, 'تحصيلات', format1)
                    worksheet.write(row, col + 6, 'تسويه د', format1)
                    worksheet.write(row, col + 7, 'رصيد اخر المده', format1)
                    worksheet.write(row, col + 8, 'التغير فى الرصيد', format1)
                    row += 1
                    for account in branch_lines_data:
                        if account.partner_id.id not in processed_partner_ids:
                            processed_partner_ids.add(account.partner_id.id)
                            filtered_accounts = balance_data.filtered(lambda x: x.partner_id == account.partner_id and x.account_id == account.partner_id.property_account_receivable_id)
                            f_in_refund_price= branch_lines_data.filtered(lambda x: x.partner_id == account.partner_id and x.debit_origin_id)
                            in_refund_price=sum([sum(move.mapped('amount_total_signed')) for move in
                                                     f_in_refund_price])

                            debit = round(sum(filtered_accounts.mapped('debit')), 4)
                            print('ddddddd',f_in_refund_price)
                            credit = round(sum(filtered_accounts.mapped('credit')), 4)
                            balance = debit

                            unit_branch = sum([sum(move.mapped('amount_total_in_currency_signed')) for move in
                                                     branch_lines_data.filtered(
                                                         lambda x: x.move_type == 'out_invoice')])


                            out_refund = self.env['account.move'].search([
                                ('move_type', '=', 'out_refund'),
                                ('partner_id', '=', account.partner_id.id),
                                ('state', '=', 'posted')
                            ])
                            out_refund_price = round(abs(sum(out_refund.mapped('amount_total_signed'))), 4)
                            filtered_payments = payment_data.filtered(lambda x: x.partner_id == account.partner_id)
                            payment = round(sum(filtered_payments.mapped('amount_company_currency_signed')), 4)
                            last_term_balance = round(abs(balance + unit_branch - payment), 4)
                            change_in_balance = round(abs(balance - last_term_balance), 4)
                            worksheet.write(row, col, account.partner_id.other_id, format4)
                            worksheet.write(row, col + 1, account.partner_id.name, format4)
                            worksheet.write(row, col + 2, debit, format4)
                            worksheet.write(row, col + 3, unit_branch, format4)
                            worksheet.write(row, col + 4, in_refund_price, format4)
                            worksheet.write(row, col + 5, payment, format4)
                            worksheet.write(row, col + 7, last_term_balance, format4)
                            worksheet.write(row, col + 6, out_refund_price, format4)
                            worksheet.write(row, col + 8, change_in_balance, format4)
                            row += 1
