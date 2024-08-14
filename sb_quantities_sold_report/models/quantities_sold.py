from odoo import models
from datetime import date


class BranchComparison(models.AbstractModel):
    _name = 'report.sb_quantities_sold_report.report_quantities_sold'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):

        for obj in partners:
            worksheet = workbook.add_worksheet('Sales Report')
            worksheet.right_to_left()
            row = 0
            col = 0
            worksheet.set_column(0, 1, 30)
            worksheet.set_column(3 , 8 , 30)
            format1 = workbook.add_format(
                {'text_wrap': True, 'font_size': 11, 'align': 'center', 'bold': True,
                 'border': 1, 'bg_color': '#CCC7BF'})
            format2 = workbook.add_format(
                {'text_wrap': True, 'font_size': 11, 'align': 'center', 'bold': False,
                 'border': 1,'bg_color':'#FFE4CF'})
            format3 = workbook.add_format(
                {'text_wrap': True, 'font_size': 10,
                 'border': 1, 'bold': False, 'align': 'center'})
            format4 = workbook.add_format(
                {'text_wrap': True, 'font_size': 12, 'align': 'center', 'bold': True})
            worksheet.set_column(2, 2, 7)

            domain = [('invoice_date', '>=', obj.date_start),
                      ('invoice_date', '<=', obj.date_end),
                      ('state', '=', 'posted'),
                      ('move_type', '=', 'out_invoice'),
                      # ('line_ids.product_id.categ_id.id','=',obj.product_category_id.ids),
                      ('branch_id','=',obj.branch_id.ids)
                      ]
            if len(obj.product_category_id) == 1 and obj.product_category_id.name == 'All':
                pass
            else:
                domain.append(('line_ids.product_id.categ_id.id', 'in', obj.product_category_id.ids))
            lines_data = self.env['account.move'].search(domain)
            existing_branch = lines_data.mapped('branch_id')
            existing_products = list(set(lines_data.mapped('line_ids.product_id')))
            print('existing_products',existing_products)


            worksheet.merge_range(row + 1, col + 2, row + 1, col + 3, 'مقارنه الكميات المباعه ', format4)
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
                worksheet.merge_range(row, col, row, col + 5, branch.name, format2)
                row += 1
                worksheet.write(row, col, 'الرقم المرجعى', format1)
                worksheet.write(row, col + 1, 'المنتج', format1)
                # worksheet.write(row, col + 2, '', format1)
                # worksheet.write(row, col + 3, 'الكميه المباعه', format1)
                worksheet.merge_range(row, col+2, row, col + 3, 'الكميه المباعه', format1)
                worksheet.write(row, col + 4, 'اجمالى الكميه المباعه', format1)
                worksheet.write(row, col + 5, 'الكميه المتاحه', format1)
                current_branch_lines = lines_data.filtered(lambda x: x.branch_id == branch)
                row += 1
                for product in existing_products:
                    product_ref = product.default_code
                    product_name = product.name

                    product_uom_name =' حبه'
                    product_qty = sum(current_branch_lines.line_ids.filtered(lambda x: x.product_id == product).mapped('quantity'))
                    domain_all_qty = [
                              ('state', '=', 'posted'),
                              ('move_type', '=', 'out_invoice'),
                              ('line_ids.product_id','=',product.id)
                              ]
                    qty_all = self.env['account.move'].search(domain_all_qty)
                    product_qty_all = sum(qty_all.line_ids.filtered(lambda x: x.product_id == product).mapped('quantity'))
                    domain_on_hand = [
                        # ('date','<',obj.date_start),
                        ('location_id.branch_id', '=', branch.id),
                        # ('branch_id','=',branch.id)
                    ]
                    on_hand = self.env['stock.quant'].search(domain_on_hand)
                    product_qty_in = round(sum(
                        on_hand.filtered(lambda x: x.product_id == product ).mapped(
                            'quantity')
                    ),4)


                    worksheet.write(row, col, product_ref, format3)
                    worksheet.write(row, col + 1,product_name, format3)
                    worksheet.write(row, col + 2, product_uom_name, format3)
                    worksheet.write(row, col + 3, product_qty, format3)
                    worksheet.write(row, col + 4, product_qty_all, format3)
                    worksheet.write(row, col + 5, product_qty_in, format3)
                    row +=1





