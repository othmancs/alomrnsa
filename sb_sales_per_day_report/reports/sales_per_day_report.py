from odoo import models


class SellerActivityReportXlsx(models.AbstractModel):
    _name = 'report.sb_sales_per_day_report.report_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet('تقرير المبيعات باليوم')
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
        company_name = data['form'].get('company_id', ['Unknown Company'])[1]
        sheet.merge_range(row, col + 4, row + 1, col + 5, company_name, format1)
        row += 2
        sheet.merge_range(row, col + 4, row + 1, col + 5, 'تقـريـر المبيعــات بـاليــوم', format1)
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

        # Table Header
        table_header = ['رقم اليوم', 'اليوم', 'التاريخ هـ', 'التاريخ م', 'المبيعات', 'الارجاعات', 'صافي المبيعات',
                        'صافي التكلفة', 'الربح']
        for i, header in enumerate(table_header):
            sheet.write(row, col + i, header, format1)
        row += 1

        # Table Content
        for branch in data['form']['branch_data']:
            sheet.merge_range(row, col + 4, row, col + 5, branch['branch_name'], format4)
            row += 1

            counter = 1  # Initialize counter for each branch
            for record in branch['records']:
                sheet.write(row, col, counter, format2)  # Write counter in the first column
                sheet.write(row, col + 1, record['day_name'], format2)
                sheet.write(row, col + 2, record['hijri_date'], format2)
                sheet.write(row, col + 3, record['invoice_date'], format2)  # 'التاريخ م' is repeated
                sheet.write(row, col + 4, record['sales'], format2)
                sheet.write(row, col + 5, record['returns'], format2)
                sheet.write(row, col + 6, abs(record['net_sales']), format2)
                sheet.write(row, col + 7, abs(record['cost']), format2)
                sheet.write(row, col + 8, abs(record['profit']), format2)
                row += 1
                counter += 1  # Increment counter

            row += 1  # Add an extra row for spacing between branches
