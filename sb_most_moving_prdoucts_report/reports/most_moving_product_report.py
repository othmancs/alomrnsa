from odoo import models

class MovingProductReportXlsx(models.AbstractModel):
    _name = 'report.sb_most_moving_prdoucts_report.report_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet('تقرير أكثر الأصناف حركة بالنسبة')
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

        row = 0
        col = 0

        # Company Information
        sheet.merge_range(row, col + 4, row + 1, col + 5, form['company_id'][1], format1)
        row += 2
        sheet.merge_range(row, col + 4, row + 1, col + 5, 'تقرير أكثر الأصناف حركة بالنسبة', format1)
        row += 2

        # Filter Information
        sheet.write(row + 1, col , ':الفــــرع', format2)
        sheet.write(row + 1, col + 1, form['branch_id'][1], format2)

        sheet.write(row + 2, col + 4, ':من تاريخ', format2)
        sheet.write(row + 2, col + 5, form['date_from'], format2)
        row += 1
        sheet.write(row + 2, col + 4, ':إلى تاريخ', format2)
        sheet.write(row + 2, col + 5, form['date_to'], format2)
        row += 1
        sheet.write(row, col, ':طبع بواسطة', format2)
        sheet.write(row, col + 1, form['printed_by'], format2)
        row += 1
        sheet.write(row, col, ':تاريخ الطباعة', format2)
        sheet.write(row, col + 1, form['print_date'], format2)
        row += 2

        # Table Header
        table_header = ['رقم الصنف', 'وصف الصنف', 'رصيد البداية', 'ادخالات الفترة', 'الكمية المباعة', 'المتوفر', 'الكمية المرتجعة', 'نسبة مئوية']
        for i, header in enumerate(table_header):
            sheet.write(row, col + i, header, format1)
        row += 1

        # Table Content
        products = form.get('products', [])
        for product in products:
            sheet.write(row, col, product.get('product_reference', ''), format2)
            sheet.write(row, col + 1, product.get('product_description', ''), format2)
            sheet.write(row, col + 2, product.get('beginning_balance', 0), format2)
            sheet.write(row, col + 3, product.get('new_incoming', 0), format2)
            sheet.write(row, col + 4, product.get('new_outgoing', 0), format2)
            sheet.write(row, col + 5, product.get('available_qty', 0), format2)
            sheet.write(row, col + 6, product.get('return_qty', 0), format2)
            sheet.write(row, col + 7, f"{product.get('sales_percentage', 0):.2f}%", format2)
            row += 1

        # Adjust column width
        sheet.set_column(col, col + len(table_header) - 1, 20)
