# -*- coding: utf-8 -*-

from odoo import models
from odoo.tools.misc import xlwt
from odoo.tools import groupby
import base64
import io


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    def send_mail_expense(self):
        all_expense_sheets = self.search([])
        for manager, sheets in groupby(self, lambda hes: hes.user_id):
            mail_expense = self.env.ref('saudi_hr_it_operations.email_template_expense_sheet_manager')
            data = self.prepare_excel_report(sheets)
            attachments = [['expense_sheet_1.xlsx', data]]
            mail_expense.with_context({'manager': manager, 'company_mail': manager.company_id.email}).send_mail(sheets[0].id, force_send=True, email_values={'email_from': manager.company_id.email, 
                                                                'email_to': manager.partner_id.email,
                                                                'attachments': attachments})
        return

    def prepare_excel_report(self, sheets):
        workbook = xlwt.Workbook(encoding="UTF-8")
        file_name = 'expense_sheet.xlsx'
        worksheet = workbook.add_sheet('Expense Report', cell_overwrite_ok=True)
        worksheet.col(1).width = 256 * 20
        worksheet.col(2).width = 256 * 20
        worksheet.col(3).width = 256 * 20
        worksheet.col(4).width = 350 * 20
        worksheet.col(5).width = 256 * 20
        worksheet.col(6).width = 256 * 20
        worksheet.col(7).width = 256 * 20
        heading_style = xlwt.easyxf("font: bold on;")
        row, column = 0, 0
        row += 7
        worksheet.write_merge(0, row, column, 3, '', heading_style)
        worksheet.write(4, 5, 'MXN$')
        worksheet.write(4, 6, 'CAD$')
        worksheet.write(5, 4, 'CAD$ Conversion Calculator')
        row += 2
        worksheet.write(row, 0, 'Date', heading_style)
        worksheet.write(row, 1, 'W/O#', heading_style)
        worksheet.write(row, 2, 'Customer/GuestName', heading_style)
        worksheet.write(row, 3, 'Receipt Description', heading_style)
        worksheet.write(row, 4, 'Receipt Type', heading_style)
        worksheet.write(row, 5, 'Receipt Amt Incl. IVA', heading_style)
        worksheet.write(row, 6, 'IVA', heading_style)
        worksheet.write(row, 7, 'Mileage KM', heading_style)
        worksheet.write(row, 8, 'Currency', heading_style)
        total_amount = 0
        for sheet in sheets:
            for rec in sheet.expense_line_ids:
                row += 1
                total_amount += rec.total_amount_company
                worksheet.write(row, 0, rec.create_date.strftime("%d/%m/%Y"))
                worksheet.write(row, 3, rec.name)
                worksheet.write(row, 4, rec.product_id.name)
                worksheet.write(row, 5, rec.total_amount_company)
                worksheet.write(row, 8, rec.currency_id.name)
        row += 1
        worksheet.write(row, 5, total_amount, heading_style)
        row += 3
        worksheet.write_merge(row, row, 0, 1, 'Expense Report', heading_style)
        row += 3
        worksheet.write_merge(row, row, 0, 1, 'Mileage', heading_style)
        worksheet.write(row, 2, 'Other Notes', heading_style)
        # worksheet.write(row, 5, total_amount, heading_style)
        fp = io.BytesIO()
        workbook.save(fp)
        fp.seek(0)
        data = base64.encodebytes(fp.read())
        fp.close()
        return data
