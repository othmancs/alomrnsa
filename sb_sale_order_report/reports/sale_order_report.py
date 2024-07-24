from odoo import models

class SaleOrderReportXlsx(models.AbstractModel):
    _name = 'report.sb_sale_order_report.report_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet('تقـريـر عـروض الاســعار')
        sheet.set_column(0, 10, 30)
        bold = workbook.add_format({'bold': True})
        format1 = workbook.add_format(
            {'text_wrap': True, 'font_size': 12, 'align': 'center', 'bold': True, 'border': 1, 'bg_color': '#CCC7BF'})
        format2 = workbook.add_format({'text_wrap': True, 'font_size': 12, 'align': 'center', 'border': 1})
        format3 = workbook.add_format(
            {'text_wrap': True, 'font_size': 15, 'align': 'center', 'bold': True, 'border': 2, 'bg_color': '#CCC7BF'})
        sheet.right_to_left()

        # Extract form data
        form = data['form']
        sale_orders = data.get('sale_order', [])

        # Separate sale orders by branch
        branch_sale_orders = {}
        for order in sale_orders:
            branch_id = order['branch_id'][0]
            branch_name = self.env['res.branch'].browse(branch_id).name
            if branch_name not in branch_sale_orders:
                branch_sale_orders[branch_name] = []
            branch_sale_orders[branch_name].append(order)

        row = 0
        col = 0

        # Company Information
        sheet.merge_range(row, col + 4, row + 1, col + 5, form['company_id'][1], format1)
        row += 2
        sheet.merge_range(row, col + 4, row + 1, col + 5, 'تقـريـر عـروض الاســعار', format1)
        row += 2

        # Filter Information
        sheet.write(row + 2, col + 4, 'مـن تـاريـخ', format2)
        sheet.write(row + 2, col + 5, form['date_from'], format2)
        row += 1
        sheet.write(row + 2, col + 4, 'الـي تـاريـخ', format2)
        sheet.write(row + 2, col + 5, form['date_to'], format2)
        row += 1
        sheet.write(row, col, 'طبـع بواسطـة:', format2)
        sheet.write(row, col + 1, form['printed_by'], format2)
        row += 1
        sheet.write(row, col, 'تـاريـخ الطبـاعـة:', format2)
        sheet.write(row, col + 1, form['print_date'], format2)
        row += 2

        # Table Header
        table_header = ['رقم العرض', 'العميل', 'البائع', 'التاريخ', 'صلاحية العرض', 'طريقة الدفع', 'الإجمالي', 'ربح متوقع', 'هامش متوقع']
        for i, header in enumerate(table_header):
            sheet.write(row, col + i, header, format1)
        row += 1

        # Table Content
        for branch_name, orders in branch_sale_orders.items():
            # Branch Name Header
            sheet.merge_range(row, col, row, col + len(table_header) - 1, f'الفرع: {branch_name}', format3)
            row += 1

            # Table Content for Each Branch
            for rec in orders:
                sheet.write(row, col, rec['name'], format2)
                sheet.write(row, col + 1, rec['partner_id'][1] if rec['partner_id'] else '', format2)
                sheet.write(row, col + 2, rec['created_by_id'][1] if rec['created_by_id'] else '', format2)
                sheet.write(row, col + 3, rec['date_order'], format2)
                sheet.write(row, col + 4, rec['validity_date'], format2)
                payment_method = rec['payment_method']
                payment_method_text = 'نقدى' if payment_method == 'option1' else 'اجل' if payment_method == 'option2' else ''
                sheet.write(row, col + 5, payment_method_text, format2)
                sheet.write(row, col + 6, rec['amount_untaxed'], format2)
                sheet.write(row, col + 7, rec['margin'], format2)
                sheet.write(row, col + 8, round(rec['margin_percent'] * 100, 2), format2)
                row += 1

            # Add space between branches
            row += 2

        # Adjust column width
        sheet.set_column(col, col + len(table_header) - 1, 20)
