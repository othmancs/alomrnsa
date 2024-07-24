from odoo import models


class SellerActivityReportXlsx(models.AbstractModel):
    _name = 'report.sb_total_seller_activity_report.report_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet('تقـريـر نشـــاطـ البـائـعيـن اجمــالـى')
        sheet.set_column(0, 17, 20)
        bold = workbook.add_format({'bold': True})
        format1 = workbook.add_format(
            {'text_wrap': True, 'font_size': 12, 'align': 'center', 'bold': True, 'border': 1, 'bg_color': '#CCC7BF'})
        format2 = workbook.add_format({'text_wrap': True, 'font_size': 12, 'align': 'center', 'border': 1})
        format3 = workbook.add_format(
            {'text_wrap': True, 'font_size': 15, 'align': 'center', 'bold': True, 'border': 2, 'bg_color': '#CCC7BF'})

        format4 = workbook.add_format(
            {'text_wrap': True, 'font_size': 12, 'align': 'center', 'bold': True, 'border': 1, 'bg_color': '#C0C0C0'})
        sheet.right_to_left()

        # Header
        row = 0
        col = 0

        # Company Information
        # sheet.merge_range(row, col + 4, row + 1, col + 5, data['form']['company_id'][1], format1)
        company_name = data['form'].get('company_id', ['Unknown Company'])
        sheet.merge_range(row, col + 4, row + 1, col + 5, company_name, format1)
        row += 2
        sheet.merge_range(row, col + 4, row + 1, col + 5, 'تقـريـر نشـــاطـ البـائـعيـن اجمــالـى', format1)
        row += 2

        # Filter Information
        branch_names = data['form'].get('branch_names', '')
        if branch_names and len(branch_names.split(',')) == 1:
            sheet.write(row, col + 4, 'الفــرع', format1)
            sheet.write(row, col + 5, branch_names, format1)
            row += 1
        else:
            sheet.write(row, col + 5, '')
            sheet.write(row, col + 6, '')
            row += 1
        sheet.write(row + 2, col + 5, 'مـن تـاريـخ', format2)
        sheet.write(row + 2, col + 6, data['form'].get('date_from', ''), format2)
        row += 1
        sheet.write(row + 2, col + 5, 'الـي تـاريـخ', format2)
        sheet.write(row + 2, col + 6, data['form'].get('date_to', ''), format2)
        row += 1
        sheet.write(row, col, 'طبـع بواسطـة:', format2)
        sheet.write(row, col + 1, data['form'].get('printed_by', ''), format2)
        row += 1
        sheet.write(row, col, 'تـاريـخ الطبـاعـة:', format2)
        sheet.write(row, col + 1, data['form'].get('print_date', ''), format2)
        row += 2

        # Merged Header Row
        sheet.merge_range(row, col + 1, row, col + 7, 'نـقـــدي', format3)
        sheet.merge_range(row, col + 8, row, col + 14, 'أجــــــل', format3)
        sheet.merge_range(row, col + 15, row, col + 17, 'اجـمـــالـــى', format3)
        row += 1

        # Table Header
        table_header = ['اسم البائع', 'المبيعات النقدية', 'كمية المبيعات النقدية', 'اجمالى الارجاعات', 'كمية الارجعات',
                        'صافى المبيعات', 'صافى التكلفة', 'ربح نقدى', 'اجمالى المبيعات الاجلة', 'كمية المبيعات الاجلة',
                        'ارجاعات المبيعات الاجلة', 'كمية ارجاعات المبيعات الاجلة', 'صافى المبيعات الاجلة',
                        'تكلفة المبيعات', 'ربح الاجل', 'صافى المبيعات الاجل + النقدى', 'صافى التكلفة', 'الربح']
        for i, header in enumerate(table_header):
            sheet.write(row, col + i, header, format1)
        row += 1

        # Initialize totals
        totals = {
            'cash_sales_total': 0,
            'cash_quantity_total': 0,
            'cash_returns_total': 0,
            'cash_returns_quantity_total': 0,
            'net_cash_sales_total': 0,
            'cash_cost_total': 0,
            'cash_profit_total': 0,
            'credit_sales_total': 0,
            'credit_quantity_total': 0,
            'credit_returns_total': 0,
            'credit_returns_quantity_total': 0,
            'net_credit_sales_total': 0,
            'credit_cost_total': 0,
            'credit_profit_total': 0,
            'total_net_sales_total': 0,
            'total_cost_total': 0,
            'total_profit_total': 0
        }

        # Table Content
        for branch in data['form']['branch_data']:
            sheet.merge_range(row, col + 4, row, col + 5, branch['branch_name'], format4)
            # sheet.write(row, col, branch['branch_name'], format3)
            row += 1

            for data in branch['created_by_data'].values():
                cash_sales = data['option1']['invoices_sum']
                cash_quantity = data['option1']['invoices_quantity']
                cash_returns = data['option1']['credit_notes_sum']
                cash_returns_quantity = data['option1']['credit_notes_quantity']
                net_cash_sales = cash_sales - cash_returns
                cash_cost = data['option1']['invoices_total_purchase_price']
                cash_profit = round(cash_cost - net_cash_sales, 2)

                credit_sales = data['option2']['invoices_sum']
                credit_quantity = data['option2']['invoices_quantity']
                credit_returns = data['option2']['credit_notes_sum']
                credit_returns_quantity = data['option2']['credit_notes_quantity']
                net_credit_sales = credit_sales - credit_returns
                credit_cost = data['option2']['invoices_total_purchase_price']
                credit_profit = round(credit_cost - net_credit_sales, 2)

                total_net_sales = net_cash_sales + net_credit_sales
                total_cost = cash_cost + credit_cost
                total_profit = round(total_net_sales - total_cost, 2)

                # Update totals
                totals['cash_sales_total'] += cash_sales
                totals['cash_quantity_total'] += cash_quantity
                totals['cash_returns_total'] += cash_returns
                totals['cash_returns_quantity_total'] += cash_returns_quantity
                totals['net_cash_sales_total'] += net_cash_sales
                totals['cash_cost_total'] += cash_cost
                totals['cash_profit_total'] += cash_profit
                totals['credit_sales_total'] += credit_sales
                totals['credit_quantity_total'] += credit_quantity
                totals['credit_returns_total'] += credit_returns
                totals['credit_returns_quantity_total'] += credit_returns_quantity
                totals['net_credit_sales_total'] += net_credit_sales
                totals['credit_cost_total'] += credit_cost
                totals['credit_profit_total'] += credit_profit
                totals['total_net_sales_total'] += total_net_sales
                totals['total_cost_total'] += total_cost
                totals['total_profit_total'] += total_profit

                # Display seller data
                sheet.write(row, col, data['name'], format2)
                sheet.write(row, col + 1, cash_sales, format2)
                sheet.write(row, col + 2, cash_quantity, format2)
                sheet.write(row, col + 3, cash_returns, format2)
                sheet.write(row, col + 4, cash_returns_quantity, format2)
                sheet.write(row, col + 5, net_cash_sales, format2)
                sheet.write(row, col + 6, cash_cost, format2)
                sheet.write(row, col + 7, cash_profit, format2)
                sheet.write(row, col + 8, credit_sales, format2)
                sheet.write(row, col + 9, credit_quantity, format2)
                sheet.write(row, col + 10, credit_returns, format2)
                sheet.write(row, col + 11, credit_returns_quantity, format2)
                sheet.write(row, col + 12, net_credit_sales, format2)
                sheet.write(row, col + 13, credit_cost, format2)
                sheet.write(row, col + 14, credit_profit, format2)
                sheet.write(row, col + 15, total_net_sales, format2)
                sheet.write(row, col + 16, total_cost, format2)
                sheet.write(row, col + 17, total_profit, format2)
                row += 1

            # Display branch totals
            sheet.write(row, col, 'الاجمالي', format1)
            sheet.write(row, col + 1, totals['cash_sales_total'], format1)
            sheet.write(row, col + 2, totals['cash_quantity_total'], format1)
            sheet.write(row, col + 3, totals['cash_returns_total'], format1)
            sheet.write(row, col + 4, totals['cash_returns_quantity_total'], format1)
            sheet.write(row, col + 5, totals['net_cash_sales_total'], format1)
            sheet.write(row, col + 6, round(totals['cash_cost_total'], 2), format1)
            sheet.write(row, col + 7, totals['cash_profit_total'], format1)
            sheet.write(row, col + 8, totals['credit_sales_total'], format1)
            sheet.write(row, col + 9, totals['credit_quantity_total'], format1)
            sheet.write(row, col + 10, totals['credit_returns_total'], format1)
            sheet.write(row, col + 11, totals['credit_returns_quantity_total'], format1)
            sheet.write(row, col + 12, totals['net_credit_sales_total'], format1)
            sheet.write(row, col + 13, round(totals['credit_cost_total'], 2), format1)
            sheet.write(row, col + 14, totals['credit_profit_total'], format1)
            sheet.write(row, col + 15, totals['total_net_sales_total'], format1)
            sheet.write(row, col + 16, round(totals['total_cost_total'], 2), format1)
            sheet.write(row, col + 17, totals['total_profit_total'], format1)
            row += 1
