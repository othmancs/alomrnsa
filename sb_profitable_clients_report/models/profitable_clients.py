from odoo import models
from datetime import date


class BranchComparison(models.AbstractModel):
    _name = 'report.sb_profitable_clients_report.report_profitable_clients'
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

            domain = [('invoice_date', '>=', obj.date_start),
                      ('invoice_date', '<=', obj.date_end),
                      ('state', '=', 'posted'),
                      ('move_type', '=', 'out_invoice'),
                      ('branch_id', '=', obj.branch_id.id)
                      ]
            lines_data = self.env['account.move'].search(domain)
            existing_client = lines_data.mapped('invoice_partner_display_name')

            worksheet.merge_range(row + 1, col + 2, row + 1, col + 3, 'العملاء الاكثر ربحيه ', format4)
            worksheet.merge_range(row, col + 2, row, col + 3, lines_data.company_id.name, format4)
            worksheet.merge_range(row + 5, col + 2, row + 5, col + 3, "الفرع", format4)
            worksheet.merge_range(row + 6, col + 2, row + 6, col + 3, obj.branch_id.name, format4)
            worksheet.write(row + 3, col + 4, ' :من ', format1)
            worksheet.write(row + 4, col + 4, '  :الى ', format1)
            worksheet.write(row + 3, col + 5, obj.date_start.strftime('%d/%m/%Y'), format3)
            worksheet.write(row + 4, col + 5, obj.date_end.strftime('%d/%m/%Y'), format3)
            worksheet.write(row + 3, col, ' :تاريخ طباعه ', format1)
            worksheet.write(row + 3, col + 1, date.today().strftime('%d/%m/%Y'), format3)
            worksheet.write(row + 4, col, ' :طبع من مستخدم  ', format1)
            worksheet.write(row + 4, col + 1, self.env.user.name, format3)

            row += 8
            worksheet.write(row, col, 'رقم العميل', format1)
            worksheet.write(row, col + 1, 'اسم العميل  ', format1)
            worksheet.write(row, col + 2, 'المبيعات', format1)
            worksheet.write(row, col + 3, 'التكلفه', format1)
            worksheet.write(row, col + 4, 'الربح', format1)
            worksheet.write(row, col + 5, 'نسبه الربح %', format1)
            row += 1
            existing_clients = set()
            total1 = 0.0
            total2 = 0.0
            total3 = 0.0
            total4 = 0.0

            for client in existing_client:
                current_client_lines = lines_data.filtered(lambda x: x.invoice_partner_display_name == client)
                if client not in existing_clients:
                    existing_clients.add(client)
                    partner = self.env['res.partner'].search([('name', '=', client)], limit=1)
                    other_id = partner.other_id
                    unit_price_branch = sum([sum(move.mapped('amount_untaxed')) for move in
                                             current_client_lines.filtered(lambda x: x.move_type != 'out_refund')])
                    total1 += unit_price_branch
                    total_cost_branch = sum(
                        [sum(move.line_ids.mapped(lambda line: line.purchase_price * line.quantity)) for move in
                         current_client_lines.filtered(lambda x: x.move_type != 'out_refund')])
                    total2 += total_cost_branch
                    print('client', client)
                    cost = abs(unit_price_branch-total_cost_branch)
                    total3 += cost
                    if total_cost_branch > 0:
                        cost_pers = (cost / total_cost_branch) * 100
                        worksheet.write(row, col + 5, cost_pers, format2)
                        total4 += cost_pers

                    else:
                        worksheet.write(row, col + 5, '-', format2)

                    worksheet.write(row, col, other_id, format2)
                    worksheet.write(row, col + 1, client, format2)
                    worksheet.write(row, col + 2, unit_price_branch, format2)
                    worksheet.write(row, col + 3, total_cost_branch, format2)
                    worksheet.write(row, col + 4, cost, format2)
                    row += 1

            worksheet.write(row+1, col+1, 'الاجمالى', format1)
            worksheet.write(row+1, col+2, total1, format2)
            worksheet.write(row+1, col+3, total2, format2)
            worksheet.write(row+1, col+4, total3, format2)
            worksheet.write(row+1, col+5, total4, format2)
