from odoo import models

class CreditNoteReportXlsx(models.AbstractModel):
    _name = 'report.sb_credit_note_report.report_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet('CreditNoteReport')
        sheet.set_column(0, 10, 30)
        bold = workbook.add_format({'bold': True})
        format1 = workbook.add_format({'text_wrap': True, 'font_size': 12, 'align': 'center', 'bold': True, 'border': 1, 'bg_color': '#CCC7BF'})
        format2 = workbook.add_format({'text_wrap': True, 'font_size': 12, 'align': 'center', 'border': 1})
        format3 = workbook.add_format({'text_wrap': True, 'font_size': 15, 'align': 'center', 'bold': True, 'border': 2, 'bg_color': '#CCC7BF'})
        sheet.right_to_left()

        # Header
        row = 0
        col = 0

        # Company Information
        sheet.merge_range(row, col + 4, row + 1, col + 5, data['form']['company_id'][1], format1)
        row += 2
        sheet.merge_range(row, col + 4, row + 1, col + 5, 'ارجـاعــات المبيـــعات', format1)
        row += 2

        # Filter Information
        sheet.write(row + 2, col + 5, 'من تاريخ', format2)
        sheet.write(row + 2, col + 6, data['form']['date_from'], format2)
        row += 1
        sheet.write(row + 2, col + 5, 'الي تاريخ', format2)
        sheet.write(row + 2, col + 6, data['form']['date_to'], format2)
        row += 1
        sheet.write(row, col, 'طبع بواسطة:', format2)
        sheet.write(row, col + 1, data['form']['printed_by'], format2)
        row += 1
        sheet.write(row, col, 'تاريخ الطباعة:', format2)
        sheet.write(row, col + 1, data['form']['print_date'], format2)
        row += 2

        # Table Header
        table_header = ['اسم الفرع', 'رقم الارجاع', 'اسم البائع', 'اسم العميل', 'تاريح الارجاع', 'اجمالى الارجاعات', 'تكلفة الارجاعات']
        for i, header in enumerate(table_header):
            sheet.write(row, col + i, header, format1)
        row += 1

        # Table Content
        for rec in data['invoice']:
            branch_name = rec['branch_id'][1] if rec['branch_id'] and isinstance(rec['branch_id'], list) and len(rec['branch_id']) > 1 else ''
            created_by = rec['created_by_id'][1] if rec['created_by_id'] and isinstance(rec['created_by_id'], list) and len(rec['created_by_id']) > 1 else ''
            partner_name = rec['partner_id'][1] if rec['partner_id'] and isinstance(rec['partner_id'], list) and len(rec['partner_id']) > 1 else ''
            sheet.write(row, col, branch_name, format2)
            sheet.write(row, col + 1, rec['name'], format2)
            sheet.write(row, col + 2, created_by, format2)
            sheet.write(row, col + 3, partner_name, format2)
            sheet.write(row, col + 4, rec['invoice_date'], format2)
            sheet.write(row, col + 5, rec['amount_untaxed'], format2)
            sheet.write(row, col + 6, rec['total_purchase_price'], format2)
            row += 1

        # Adjust column width
        sheet.set_column(col, col + len(table_header) - 1, 20)
