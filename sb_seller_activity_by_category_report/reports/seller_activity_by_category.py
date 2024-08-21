from odoo import models


class SellerActivityReportXlsx(models.AbstractModel):
    _name = 'report.sb_seller_activity_by_category_report.report_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        for obj in partners:
            print("for obj in partners:", obj)
            print('product_category_ids',obj.product_category_ids)
            print('printed_by',obj.printed_by)
            sheet = workbook.add_worksheet('تقـريـر نشـــاطـ البـائـعيـن حســــب الفئـــات - اجمــالـى')
            sheet.set_column(0, 17, 20)

            # Define formats
            format_header = workbook.add_format({
                'text_wrap': True, 'font_size': 12, 'align': 'center', 'bold': True, 'border': 1, 'bg_color': '#CCC7BF'
            })
            format_header_title = workbook.add_format({
                'text_wrap': True, 'font_size': 14, 'align': 'center', 'bold': True, 'border': 3 , 'bg_color': '#C0C0C0'
            })
            format_subheader = workbook.add_format({
                'text_wrap': True, 'font_size': 12, 'align': 'center', 'border': 1
            })
            format_section_title = workbook.add_format({
                'text_wrap': True, 'font_size': 12, 'align': 'center', 'bold': True, 'border': 1, 'bg_color': '#C0C0C0'
            })
            format_branch_title = workbook.add_format({
                'text_wrap': True, 'font_size': 12, 'align': 'center', 'bold': True, 'border': 1, 'bg_color': '#b0c6c0'
            })
            format_created_title = workbook.add_format({
                'text_wrap': True, 'font_size': 12, 'align': 'center', 'bold': True, 'border': 1, 'bg_color': '#b1adc3'
            })
            format_rows = workbook.add_format({
                'text_wrap': True, 'font_size': 12, 'align': 'center', 'bold': True, 'border': 1,
            })
            format_data = workbook.add_format({
                'text_wrap': True, 'font_size': 12, 'align': 'center', 'border': 1
            })
            sheet.right_to_left()

            # Header
            row = 0
            col = 0

            # Company Information
            company_name = obj.company_id.name
            sheet.merge_range(row, col + 4, row + 1, col + 5, str(company_name), format_header)
            row += 2
            sheet.merge_range(row, col + 4, row + 1, col + 5, 'تقـريـر نشـــاطـ البـائـعيـن حســــب الفئـــات - اجمــالـى', format_header)
            row += 2

            sheet.write(row + 2, col + 5, 'مـن تـاريـخ', format_subheader)
            sheet.write(row + 2, col + 6, obj.date_from.strftime('%d/%m/%Y'), format_subheader)
            row += 1
            sheet.write(row + 2, col + 5, 'الـي تـاريـخ', format_subheader)
            sheet.write(row + 2, col + 6, obj.date_to.strftime('%d/%m/%Y'), format_subheader)
            row += 1
            sheet.write(row, col, 'طبـع بواسطـة:', format_subheader)
            sheet.write(row, col + 1, obj.printed_by, format_subheader)
            row += 1
            sheet.write(row, col, 'تـاريـخ الطبـاعـة:', format_subheader)
            sheet.write(row, col + 1, obj.print_date.strftime('%d/%m/%Y'), format_subheader)
            row += 2

            # Merged Header Row
            sheet.merge_range(row, col + 1, row, col + 7, 'نـقـــدي', format_header_title)
            sheet.merge_range(row, col + 8, row, col + 14, 'أجــــــل', format_header_title)
            sheet.merge_range(row, col + 15, row, col + 17, 'اجـمـــالـــى', format_header_title)
            row += 1

            sheet.merge_range(row - 1, col, row, col, 'الفئـة', format_section_title)
            sheet.write(row, col + 1, 'المبيعات النقدية', format_section_title)
            sheet.write(row, col + 2, 'كمية المبيعات النقدية', format_section_title)
            sheet.write(row, col + 3, 'اجمالى الارجاعات', format_section_title)
            sheet.write(row, col + 4, 'كمية الارجاعات', format_section_title)
            sheet.write(row, col + 5, 'صافى المبيعات', format_section_title)
            sheet.write(row, col + 6, 'صافى التكلفة', format_section_title)
            sheet.write(row, col + 7, 'ربـح نقــدي', format_section_title)
            sheet.write(row, col + 8, 'اجمالى المبيعات الاجلة', format_section_title)
            sheet.write(row, col + 9, 'كمية المبيعات الاجلة', format_section_title)
            sheet.write(row, col + 10, 'ارجاعات المبيعات الاجلة', format_section_title)
            sheet.write(row, col + 11, 'كمية ارجاعات المبيعات الاجلة', format_section_title)
            sheet.write(row, col + 12, 'صافى المبيعات الاجلة', format_section_title)
            sheet.write(row, col + 13, 'تكلفة المبيعات', format_section_title)
            sheet.write(row, col + 14, 'ربح الاجل', format_section_title)
            sheet.write(row, col + 15, 'صافــي التكلفــة نقــد/آجــل', format_section_title)
            sheet.write(row, col + 16, 'صافى التكلفة', format_section_title)
            sheet.write(row, col + 17, 'الربــــح', format_section_title)
            row += 1
            domain = [('invoice_date', '>=', obj.date_from),
                      ('invoice_date', '<=', obj.date_to),
                      ('move_type', 'in', ['out_invoice', 'out_refund']),
                      ('state', '=', 'posted'),
                      ('branch_id', 'in', obj.branch_ids.ids),
                      ('invoice_line_ids.product_id.categ_id', 'in', obj.product_category_ids.ids)]

            # Append created_by_id to domain if provided
            if obj.created_by_id:
                domain.append(('created_by_id', 'in', obj.created_by_id.ids))

            lines_data = self.env['account.move'].search(domain)

            existing_branches = lines_data.mapped('branch_id')
            existing_created = list(set(lines_data.mapped('created_by_id')))
            existing_category = list(set(lines_data.mapped('invoice_line_ids.product_id.categ_id')))

            branches = [{'branch_id': branch.id, 'branch_name': branch.name} for branch in existing_branches]
            created_d = {invoice.created_by_id.id: {'branch_name': invoice.branch_id.name,
                                                    'created_by_name': invoice.created_by_id.name} for invoice in
                         lines_data}
            created = list(created_d.values())

            report_data = {}

            for branch in existing_branches:
                current_branch_lines = lines_data.filtered(lambda x: x.branch_id == branch)
                sheet.merge_range(row, col, row, col + 17, branch.name, format_branch_title)
                row += 1
                if current_branch_lines:
                    for created_by in (obj.created_by_id or existing_created):
                        # Flag to track if the name has been written for this created_by
                        name_written = False

                        current_created_lines = current_branch_lines.filtered(
                            lambda x: x.created_by_id == created_by and x.branch_id == branch
                        )
                        current_lines = current_created_lines.invoice_line_ids.filtered(
                            lambda
                                x: x.move_id.created_by_id == created_by and x.move_id.branch_id == branch and x.product_id.categ_id in obj.product_category_ids
                        )
                        for line in current_lines:
                            sum_total_option1_branch_price = 0.0
                            sum_total_quantity_option1 = 0.0
                            sum_total_option1_branch_price_credit = 0.0
                            sum_total_quantity_option1_credit = 0.0
                            sum_net_sales_option1 = 0.0
                            sum_total_option1_branch_purchase = 0.0
                            sum_cash_profit_option1 = 0.0
                            sum_total_option2_branch_price = 0.0
                            sum_total_quantity_option2 = 0.0
                            sum_total_option2_branch_price_credit = 0.0
                            sum_total_quantity_option2_credit = 0.0
                            sum_net_sales_option2 = 0.0
                            sum_total_option2_branch_purchase = 0.0
                            sum_cash_profit_option2 = 0.0
                            sum_net_sales_cash_credit = 0.0
                            sum_net_cost_cash_credit = 0.0
                            sum_profit = 0.0

                            if not name_written:
                                created_name = created_by.name if obj.created_by_id else created_by.name
                                sheet.merge_range(row, col, row, col + 17, created_name, format_created_title)
                                row += 1
                                name_written = True

                        if current_created_lines:
                            for category in obj.product_category_ids:
                                total_option1_branch_purchase = 0.0
                                total_option2_branch_purchase = 0.0
                                total_option1_branch_price = 0.0
                                total_option2_branch_price = 0.0
                                total_quantity_option1 = 0.0
                                total_quantity_option2 = 0.0
                                total_option1_branch_purchase_credit = 0.0
                                total_option2_branch_purchase_credit = 0.0
                                total_option1_branch_price_credit = 0.0
                                total_option2_branch_price_credit = 0.0
                                total_quantity_option1_credit = 0.0
                                total_quantity_option2_credit = 0.0
                                net_sales_option1 = 0.0
                                cash_profit_option1 = 0.0
                                net_sales_option2 = 0.0
                                cash_profit_option2 = 0.0
                                net_sales_cash_credit = 0.0
                                net_cost_cash_credit = 0.0
                                profit = 0.0

                                current_category_lines = current_lines.filtered(
                                    lambda x: x.product_id.categ_id == category
                                )

                                if current_category_lines:
                                    sheet.write(row, col, category.name, format_section_title)
                                    total_option1_branch_purchase = sum(
                                        [sum(move.mapped(lambda x: x.purchase_price * x.quantity)) for move in
                                         current_category_lines.filtered(lambda
                                                                             x: x.move_id.payment_method == 'option1' and x.move_type == 'out_invoice')]
                                    )
                                    total_option2_branch_purchase = sum(
                                        [sum(move.mapped(lambda x: x.purchase_price * x.quantity)) for move in
                                         current_category_lines.filtered(lambda
                                                                             x: x.move_id.payment_method == 'option2' and x.move_type == 'out_invoice')]
                                    )
                                    total_option1_branch_price = sum(
                                        [sum(move.mapped(lambda x: x.price_unit * x.quantity)) for move in
                                         current_category_lines.filtered(lambda
                                                                             x: x.move_id.payment_method == 'option1' and x.move_type == 'out_invoice')]
                                    )
                                    total_option2_branch_price = sum(
                                        [sum(move.mapped(lambda x: x.price_unit * x.quantity)) for move in
                                         current_category_lines.filtered(lambda
                                                                             x: x.move_id.payment_method == 'option2' and x.move_type == 'out_invoice')]
                                    )

                                    total_quantity_option1 = sum(
                                        current_category_lines.filtered(lambda
                                                                            x: x.move_id.payment_method == 'option1' and x.move_type == 'out_invoice').mapped(
                                            'quantity')
                                    )

                                    total_quantity_option2 = sum(
                                        current_category_lines.filtered(lambda
                                                                            x: x.move_id.payment_method == 'option2' and x.move_type == 'out_invoice').mapped(
                                            'quantity')
                                    )

                                    total_option1_branch_purchase_credit = sum(
                                        [sum(move.mapped(lambda x: x.purchase_price * x.quantity)) for move in
                                         current_category_lines.filtered(lambda
                                                                             x: x.move_id.payment_method == 'option1' and x.move_type == 'out_refund')]
                                    )
                                    total_option2_branch_purchase_credit = sum(
                                        [sum(move.mapped(lambda x: x.purchase_price * x.quantity)) for move in
                                         current_category_lines.filtered(lambda
                                                                             x: x.move_id.payment_method == 'option2' and x.move_type == 'out_refund')]
                                    )
                                    total_option1_branch_price_credit = sum(
                                        [sum(move.mapped(lambda x: x.price_unit * x.quantity)) for move in
                                         current_category_lines.filtered(lambda
                                                                             x: x.move_id.payment_method == 'option1' and x.move_type == 'out_refund')]
                                    )
                                    total_option2_branch_price_credit = sum(
                                        [sum(move.mapped(lambda x: x.price_unit * x.quantity)) for move in
                                         current_category_lines.filtered(lambda
                                                                             x: x.move_id.payment_method == 'option2' and x.move_type == 'out_refund')]
                                    )

                                    total_quantity_option1_credit = sum(
                                        current_category_lines.filtered(lambda
                                                                            x: x.move_id.payment_method == 'option1' and x.move_type == 'out_refund').mapped(
                                            'quantity')
                                    )

                                    total_quantity_option2_credit = sum(
                                        current_category_lines.filtered(lambda
                                                                            x: x.move_id.payment_method == 'option2' and x.move_type == 'out_refund').mapped(
                                            'quantity')
                                    )

                                    # ========= for option 1 ===================
                                    net_sales_option1 = total_option1_branch_price - total_option1_branch_price_credit
                                    cash_profit_option1 = total_option1_branch_purchase - net_sales_option1
                                    # ========= for option 2 ===================
                                    net_sales_option2 = total_option2_branch_price - total_option2_branch_price_credit
                                    cash_profit_option2 = total_option2_branch_purchase - net_sales_option2
                                    # ========= for profit ===================
                                    net_sales_cash_credit = net_sales_option1 + net_sales_option2
                                    net_cost_cash_credit = total_option1_branch_purchase + total_option2_branch_purchase
                                    profit = net_sales_cash_credit - net_cost_cash_credit

                                    # ==================sheet write++++++++++++++++++++++++++++++++============
                                    sheet.write(row, col + 1, round(abs(total_option1_branch_price), 2), format_rows)
                                    sheet.write(row, col + 2, total_quantity_option1, format_rows)
                                    sheet.write(row, col + 3, round(abs(total_option1_branch_price_credit), 2),
                                                format_rows)
                                    sheet.write(row, col + 4, total_quantity_option1_credit, format_rows)
                                    sheet.write(row, col + 5, round(abs(net_sales_option1), 2), format_rows)
                                    sheet.write(row, col + 6, round(abs(total_option1_branch_purchase), 2), format_rows)
                                    sheet.write(row, col + 7, round(abs(cash_profit_option1), 2), format_rows)
                                    sheet.write(row, col + 8, round(abs(total_option2_branch_price), 2), format_rows)
                                    sheet.write(row, col + 9, total_quantity_option2, format_rows)
                                    sheet.write(row, col + 10, round(abs(total_option2_branch_price_credit), 2),
                                                format_rows)
                                    sheet.write(row, col + 11, total_quantity_option2_credit, format_rows)
                                    sheet.write(row, col + 12, round(abs(net_sales_option2), 2), format_rows)
                                    sheet.write(row, col + 13, round(abs(total_option2_branch_purchase), 2),
                                                format_rows)
                                    sheet.write(row, col + 14, round(abs(cash_profit_option2), 2), format_rows)
                                    sheet.write(row, col + 15, round(abs(net_sales_cash_credit), 2), format_rows)
                                    sheet.write(row, col + 16, round(abs(net_cost_cash_credit), 2), format_rows)
                                    sheet.write(row, col + 17, round(abs(profit), 2), format_rows)
                                    sum_total_option1_branch_price += total_option1_branch_price

                                    sum_total_quantity_option1 += total_quantity_option1

                                    sum_total_option1_branch_price_credit += total_option1_branch_price_credit

                                    sum_total_quantity_option1_credit += total_quantity_option1_credit

                                    sum_net_sales_option1 += net_sales_option1

                                    sum_total_option1_branch_purchase += total_option1_branch_purchase

                                    sum_cash_profit_option1 += round(abs(cash_profit_option1), 2)

                                    sum_total_option2_branch_price += total_option2_branch_price

                                    sum_total_quantity_option2 += total_quantity_option2
                                    sum_total_option2_branch_price_credit += total_option2_branch_price_credit

                                    sum_total_quantity_option2_credit += total_quantity_option2_credit

                                    sum_net_sales_option2 += net_sales_option2

                                    sum_total_option2_branch_purchase += total_option2_branch_purchase

                                    sum_cash_profit_option2 += round(abs(cash_profit_option2), 2)

                                    sum_net_sales_cash_credit += net_sales_cash_credit

                                    sum_net_cost_cash_credit += round(abs(net_cost_cash_credit), 2)
                                    sum_profit += round(abs(profit), 2)

                                    row += 1
                                sheet.write(row, col, "الاجمالي", format_section_title)
                                sheet.write(row, col + 1, round(abs(sum_total_option1_branch_price), 2),
                                            format_section_title)
                                sheet.write(row, col + 2, sum_total_quantity_option1, format_section_title)
                                sheet.write(row, col + 3, round(abs(sum_total_option1_branch_price_credit), 2),
                                            format_section_title)
                                sheet.write(row, col + 4, sum_total_quantity_option1_credit, format_section_title)
                                sheet.write(row, col + 5, round(abs(sum_net_sales_option1), 2), format_section_title)
                                sheet.write(row, col + 6, round(abs(sum_total_option1_branch_purchase), 2),
                                            format_section_title)
                                sheet.write(row, col + 7, round(abs(sum_cash_profit_option1), 2), format_section_title)
                                sheet.write(row, col + 8, round(abs(sum_total_option2_branch_price), 2),
                                            format_section_title)
                                sheet.write(row, col + 9, sum_total_quantity_option2, format_section_title)
                                sheet.write(row, col + 10, round(abs(sum_total_option2_branch_price_credit), 2),
                                            format_section_title)
                                sheet.write(row, col + 11, sum_total_quantity_option2_credit, format_section_title)
                                sheet.write(row, col + 12, round(abs(sum_net_sales_option2), 2), format_section_title)
                                sheet.write(row, col + 13, round(abs(sum_total_option2_branch_purchase), 2),
                                            format_section_title)
                                sheet.write(row, col + 14, round(abs(sum_cash_profit_option2), 2), format_section_title)
                                sheet.write(row, col + 15, round(abs(sum_net_sales_cash_credit), 2),
                                            format_section_title)
                                sheet.write(row, col + 16, round(abs(sum_net_cost_cash_credit), 2),
                                            format_section_title)
                                sheet.write(row, col + 17, round(abs(sum_profit), 2), format_section_title)
                            row += 1



#=======================================================
#===========================================================================================
#======================================================================================================================

#             domain = [('invoice_date', '>=', obj.date_from),
#                       ('invoice_date', '<=', obj.date_to),
#                       ('move_type', 'in', ['out_invoice', 'out_refund']),
#                       ('state', '=', 'posted'),
#                       ('branch_id', 'in', obj.branch_ids.ids),
#                       ('invoice_line_ids.product_id.categ_id', 'in', obj.product_category_ids.ids)]
#
#             if obj.created_by_id.ids:
#                 domain.append(('created_by_id', 'in', obj.created_by_id.ids))
#
#             lines_data = self.env['account.move'].search(domain)
#
#             existing_branches = lines_data.mapped('branch_id')
#
#             existing_created = list(set(lines_data.mapped('created_by_id')))
#
#             existing_category = list(set(lines_data.mapped('invoice_line_ids.product_id.categ_id')))
#             print('existing_category',existing_category)
#             branches = [{'branch_id': branch.id, 'branch_name': branch.name} for branch in existing_branches]
#             created_d = {invoice.created_by_id.id: {'branch_name': invoice.branch_id.name,
#                                                     'created_by_name': invoice.created_by_id.name} for invoice in lines_data}
#             created = list(created_d.values())
#
#             report_data = {}
#
#             for branch in existing_branches:
#                 current_branch_lines = lines_data.filtered(lambda x: x.branch_id == branch)
#                 sheet.merge_range(row, col, row, col + 17, branch.name, format_branch_title)
#                 row += 1
#                 if current_branch_lines:
#                     for created_by in obj.created_by_id:
#                         # Flag to track if the name has been written for this created_by
#                         name_written = False
#
#                         current_created_lines = current_branch_lines.filtered(
#                             lambda x: x.created_by_id == created_by and x.branch_id == branch)
#                         current_lines = current_created_lines.invoice_line_ids.filtered(
#                             lambda
#                                 x: x.move_id.created_by_id == created_by and x.move_id.branch_id == branch and x.product_id.categ_id in obj.product_category_ids )
#                         print("Current lines", current_lines)
#
#                         print("current_created_lines", current_created_lines)
#                         for line in current_lines:
#                             sum_total_option1_branch_price = 0.0
#                             sum_total_quantity_option1 = 0.0
#                             sum_total_option1_branch_price_credit = 0.0
#                             sum_total_quantity_option1_credit = 0.0
#                             sum_net_sales_option1 = 0.0
#                             sum_total_option1_branch_purchase = 0.0
#                             sum_cash_profit_option1 = 0.0
#                             sum_total_option2_branch_price = 0.0
#                             sum_total_quantity_option2 = 0.0
#                             sum_total_option2_branch_price_credit = 0.0
#                             sum_total_quantity_option2_credit = 0.0
#                             sum_net_sales_option2 = 0.0
#                             sum_total_option2_branch_purchase = 0.0
#                             sum_cash_profit_option2 = 0.0
#                             sum_net_sales_cash_credit = 0.0
#                             sum_net_cost_cash_credit = 0.0
#                             sum_profit = 0.0
#
#                             # Write the name only once for each created_by
#                             if not name_written:
#                                 created_name = created_by.name
#                                 sheet.merge_range(row, col, row, col + 17, line.move_id.created_by_id.name, format_created_title)
#                                 row += 1
#                                 name_written = True
#
#                         if current_created_lines:
#                             for category in obj.product_category_ids:
#                                 total_option1_branch_purchase = 0.0
#                                 total_option2_branch_purchase = 0.0
#                                 total_option1_branch_price = 0.0
#                                 total_option2_branch_price = 0.0
#                                 total_quantity_option1 = 0.0
#                                 total_quantity_option2 = 0.0
#                                 total_option1_branch_purchase_credit = 0.0
#                                 total_option2_branch_purchase_credit = 0.0
#                                 total_option1_branch_price_credit = 0.0
#                                 total_option2_branch_price_credit = 0.0
#                                 total_quantity_option1_credit = 0.0
#                                 total_quantity_option2_credit = 0.0
#                                 net_sales_option1 = 0.0
#                                 cash_profit_option1 = 0.0
#                                 net_sales_option2 = 0.0
#                                 cash_profit_option2 = 0.0
#                                 net_sales_cash_credit = 0.0
#                                 net_cost_cash_credit = 0.0
#                                 profit = 0.0
#
#                                 current_category_lines = current_lines.filtered(lambda
#                                                                                     x: x.product_id.categ_id == category and x.move_id.branch_id == branch and x.move_id.created_by_id == created_by and x.product_id.categ_id.id in obj.product_category_ids.ids)
#                                 print('sssssssssss', current_category_lines)
#
#                                 if current_category_lines:
#                                     sheet.write(row, col, category.name, format_section_title)
#                                     total_option1_branch_purchase = sum(
#                                         [sum(move.mapped(lambda x: x.purchase_price * x.quantity)) for move in
#                                          current_category_lines.filtered(lambda
#                                                                              x: x.move_id.payment_method == 'option1' and x.move_type == 'out_invoice')])
#                                     total_option2_branch_purchase = sum(
#                                         [sum(move.mapped(lambda x: x.purchase_price * x.quantity)) for move in
#                                          current_category_lines.filtered(lambda
#                                                                              x: x.move_id.payment_method == 'option2' and x.move_type == 'out_invoice')])
#                                     total_option1_branch_price = sum(
#                                         [sum(move.mapped(lambda x: x.price_unit * x.quantity)) for move in
#                                          current_category_lines.filtered(lambda
#                                                                              x: x.move_id.payment_method == 'option1' and x.move_type == 'out_invoice')])
#                                     total_option2_branch_price = sum(
#                                         [sum(move.mapped(lambda x: x.price_unit * x.quantity)) for move in
#                                          current_category_lines.filtered(lambda
#                                                                              x: x.move_id.payment_method == 'option2' and x.move_type == 'out_invoice')])
#
#                                     total_quantity_option1 = sum(
#                                         current_category_lines.filtered(lambda
#                                                                             x: x.move_id.payment_method == 'option1' and x.move_type == 'out_invoice').mapped(
#                                             'quantity'))
#
#                                     total_quantity_option2 = sum(
#                                         current_category_lines.filtered(lambda
#                                                                             x: x.move_id.payment_method == 'option2' and x.move_type == 'out_invoice').mapped(
#                                             'quantity'))
#
#                                     total_option1_branch_purchase_credit = sum(
#                                         [sum(move.mapped(lambda x: x.purchase_price * x.quantity)) for move in
#                                          current_category_lines.filtered(
#                                              lambda
#                                                  x: x.move_id.payment_method == 'option1' and x.move_type == 'out_refund')])
#                                     total_option2_branch_purchase_credit = sum(
#                                         [sum(move.mapped(lambda x: x.purchase_price * x.quantity)) for move in
#                                          current_category_lines.filtered(
#                                              lambda
#                                                  x: x.move_id.payment_method == 'option2' and x.move_type == 'out_refund')])
#                                     total_option1_branch_price_credit = sum(
#                                         [sum(move.mapped(lambda x: x.price_unit * x.quantity)) for move in
#                                          current_category_lines.filtered(
#                                              lambda
#                                                  x: x.move_id.payment_method == 'option1' and x.move_type == 'out_refund')])
#                                     total_option2_branch_price_credit = sum(
#                                         [sum(move.mapped(lambda x: x.price_unit * x.quantity)) for move in
#                                          current_category_lines.filtered(
#                                              lambda
#                                                  x: x.move_id.payment_method == 'option2' and x.move_type == 'out_refund')])
#
#                                     total_quantity_option1_credit = sum(
#                                         current_category_lines.filtered(lambda
#                                                                             x: x.move_id.payment_method == 'option1' and x.move_type == 'out_refund').mapped(
#                                             'quantity'))
#
#                                     total_quantity_option2_credit = sum(
#                                         current_category_lines.filtered(lambda
#                                                                             x: x.move_id.payment_method == 'option2' and x.move_type == 'out_refund').mapped(
#                                             'quantity'))
#
#                                     # ========= for option 1 ===================
#                                     net_sales_option1 = total_option1_branch_price - total_option1_branch_price_credit
#                                     cash_profit_option1 = total_option1_branch_purchase - net_sales_option1
#                                     # ========= for option 2 ===================
#                                     net_sales_option2 = total_option2_branch_price - total_option2_branch_price_credit
#                                     cash_profit_option2 = total_option2_branch_purchase - net_sales_option2
#                                     # ========= for profit ===================
#                                     net_sales_cash_credit = net_sales_option1 + net_sales_option2
#                                     net_cost_cash_credit = total_option1_branch_purchase + total_option2_branch_purchase
#                                     profit = net_sales_cash_credit - net_cost_cash_credit
#
#                                     # ==================sheet write++++++++++++++++++++++++++++++++============
#                                     sheet.write(row, col + 1, round(abs(total_option1_branch_price), 2), format_rows)
#                                     sheet.write(row, col + 2, total_quantity_option1, format_rows)
#                                     sheet.write(row, col + 3, round(abs(total_option1_branch_price_credit), 2), format_rows)
#                                     sheet.write(row, col + 4, total_quantity_option1_credit, format_rows)
#                                     sheet.write(row, col + 5, round(abs(net_sales_option1), 2), format_rows)
#                                     sheet.write(row, col + 6, round(abs(total_option1_branch_purchase), 2), format_rows)
#                                     sheet.write(row, col + 7, round(abs(cash_profit_option1), 2), format_rows)
#                                     sheet.write(row, col + 8, round(abs(total_option2_branch_price), 2), format_rows)
#                                     sheet.write(row, col + 9, total_quantity_option2, format_rows)
#                                     sheet.write(row, col + 10, round(abs(total_option2_branch_price_credit), 2), format_rows)
#                                     sheet.write(row, col + 11, total_quantity_option2_credit, format_rows)
#                                     sheet.write(row, col + 12, round(abs(net_sales_option2), 2), format_rows)
#                                     sheet.write(row, col + 13, round(abs(total_option2_branch_purchase), 2), format_rows)
#                                     sheet.write(row, col + 14, round(abs(cash_profit_option2), 2), format_rows)
#                                     sheet.write(row, col + 15, round(abs(net_sales_cash_credit), 2), format_rows)
#                                     sheet.write(row, col + 16, round(abs(net_cost_cash_credit), 2), format_rows)
#                                     sheet.write(row, col + 17, round(abs(profit), 2), format_rows)
#
#                                 sum_total_option1_branch_price += total_option1_branch_price
#
#                                 sum_total_quantity_option1 += total_quantity_option1
#
#                                 sum_total_option1_branch_price_credit += total_option1_branch_price_credit
#
#                                 sum_total_quantity_option1_credit += total_quantity_option1_credit
#
#                                 sum_net_sales_option1 += net_sales_option1
#
#                                 sum_total_option1_branch_purchase += total_option1_branch_purchase
#
#                                 sum_cash_profit_option1 += cash_profit_option1
#
#                                 sum_total_option2_branch_price += total_option2_branch_price
#
#                                 sum_total_quantity_option2 += total_quantity_option2
#                                 sum_total_option2_branch_price_credit += total_option2_branch_price_credit
#
#                                 sum_total_quantity_option2_credit += total_quantity_option2_credit
#
#                                 sum_net_sales_option2 += net_sales_option2
#
#                                 sum_total_option2_branch_purchase += total_option2_branch_purchase
#
#                                 sum_cash_profit_option2 += cash_profit_option2
#
#                                 sum_net_sales_cash_credit += net_sales_cash_credit
#
#                                 sum_net_cost_cash_credit += net_cost_cash_credit
#                                 sum_profit += profit
#
#                                 row += 1
#                     sheet.write(row, col, "الاجمالي", format_section_title)
#                     sheet.write(row, col + 1, round(abs(sum_total_option1_branch_price), 2), format_section_title)
#                     sheet.write(row, col + 2, sum_total_quantity_option1, format_section_title)
#                     sheet.write(row, col + 3, round(abs(sum_total_option1_branch_price_credit), 2), format_section_title)
#                     sheet.write(row, col + 4, sum_total_quantity_option1_credit, format_section_title)
#                     sheet.write(row, col + 5, round(abs(sum_net_sales_option1), 2), format_section_title)
#                     sheet.write(row, col + 6, round(abs(sum_total_option1_branch_purchase), 2), format_section_title)
#                     sheet.write(row, col + 7, round(abs(sum_cash_profit_option1), 2), format_section_title)
#                     sheet.write(row, col + 8, round(abs(sum_total_option2_branch_price), 2), format_section_title)
#                     sheet.write(row, col + 9, sum_total_quantity_option2, format_section_title)
#                     sheet.write(row, col + 10, round(abs(sum_total_option2_branch_price_credit), 2), format_section_title)
#                     sheet.write(row, col + 11, sum_total_quantity_option2_credit, format_section_title)
#                     sheet.write(row, col + 12, round(abs(sum_net_sales_option2), 2), format_section_title)
#                     sheet.write(row, col + 13, round(abs(sum_total_option2_branch_purchase), 2), format_section_title)
#                     sheet.write(row, col + 14, round(abs(sum_cash_profit_option2), 2), format_section_title)
#                     sheet.write(row, col + 15, round(abs(sum_net_sales_cash_credit), 2), format_section_title)
#                     sheet.write(row, col + 16, round(abs(sum_net_cost_cash_credit), 2), format_section_title)
#                     sheet.write(row, col + 17, round(abs(sum_profit), 2), format_section_title)
#                 row += 1
#=====================================================
#============================================================================================
#======================================================================================================================