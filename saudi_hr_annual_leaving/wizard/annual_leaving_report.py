# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import base64
from odoo import api, fields, models, _
import io
import xlwt
from odoo.exceptions import Warning


class AnnualLeavingReport(models.TransientModel):
    _name = 'annual.leaves.report'
    _description = 'Annual Report Wizard'

    filename = fields.Char(string='File Name', size=64)
    excel_file = fields.Binary(string='Excel File')

    def generate_annual_leave_excel_report(self):
        try:
            format0 = xlwt.easyxf('font:height 230, bold True; pattern: pattern solid, fore-colour gray25; align:vert center, horiz center; borders: top_color black, bottom_color black, right_color black, left_color black,\
                left thin, right thin, top thin, bottom thin;')
            format1 = xlwt.easyxf('font:height 230, bold True; pattern: pattern solid, fore_colour gray25; align:vert center, horiz left;borders: top_color black, bottom_color black, right_color black, left_color black,\
                left thin, right thin, top thin, bottom thin;')
            format2 = xlwt.easyxf('font:height 230, bold False; pattern: pattern solid, fore_colour white; align:vert center, horiz left;borders: top_color black, bottom_color black, right_color black, left_color black,\
                left thin, right thin, top thin, bottom thin;')
            workbook = xlwt.Workbook()
            leave_ids = self.env['annual.leaving'].browse(self._context.get('active_ids') or 0)
            for leave_id in leave_ids:
                if leave_id.year_id.name == '/':
                    sheet = workbook.add_sheet(leave_id.ref or '/')
                else:
                    sheet = workbook.add_sheet(leave_id.year_id.name)
                row = 3
                column = 0
                sheet.write_merge(0, 0, 0, 6, 'Company Name : ' + self.env.user.company_id.name, format0)
                sheet.write_merge(1, 1, 0, 6, 'Year : ' + leave_id.year_id.name, format0)
                sheet.col(0).width = 256 * 15
                sheet.write(row, column, 'Employee', format1)
                sheet.col(1).width = 256 * 15
                sheet.write(row, column+1, 'Office', format1)
                sheet.col(2).width = 256 * 20
                sheet.write(row, column+2, 'Allocated Leaves', format1)
                sheet.col(3).width = 256 * 20
                sheet.write(row, column+3, 'Updated Leaves', format1)
                sheet.col(4).width = 256 * 20
                sheet.write(row, column+4, 'Used Leaves', format1)
                sheet.col(5).width = 256 * 25
                sheet.write(row, column+5, 'Encashment Leaves', format1)
                sheet.col(6).width = 256 * 25
                sheet.write(row, column+6, 'Remaining Leaves', format1)
                row += 1
                for line in leave_id.leaves_details_ids:
                    sheet.write(row, column, line.employee_id.name or '', format2)
                    sheet.write(row, column+1, line.branch_id.name or '', format2)
                    sheet.write(row, column+2, line.allocated_leaves or '0.00', format2)
                    sheet.write(row, column+3, line.updated_leaves or '0.00', format2)
                    sheet.write(row, column+4, line.used_leaves or '0.00', format2)
                    sheet.write(row, column+5, line.encashment_leaves or '0.00', format2)
                    sheet.write(row, column+6, line.remaining_leaves or '0.00', format2)
                    row += 1
                row += 1

            filename = ("Annual Leaving Report.xls")
            fp = io.BytesIO()
            workbook.save(fp)
            fp.seek(0)
            data_of_file = fp.read()
            fp.close()
            out = base64.encodebytes(data_of_file)
            self.write({'excel_file': out, 'filename': filename})
            return self.return_wiz_action(self.id)

        except Exception as e:
            raise Warning(_('You are not able to print this report please contact your '
                            'administrator : %s ' % str(e)))

    def return_wiz_action(self, res_id, context=None):
        """
            Return Admin Reports
        """
        return {
            'name': 'Annual Leaves Report',
            'res_id': res_id,
            'res_model': 'annual.leaves.report',
            'view_mode': 'form',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new',
        }
