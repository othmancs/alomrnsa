# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.tools.misc import format_date as odoo_format_date
from dateutil.relativedelta import relativedelta
from io import BytesIO
import xlsxwriter
import base64


class LeaveTrackerReports(models.TransientModel):
    _name = "leave.tracker.wizard"
    _description = "Leave Tracker Wizard"

    @api.model
    def default_get(self, default_fields):
        """ Override method for update default values """
        res = super(LeaveTrackerReports, self).default_get(default_fields)
        res.update({
                'start_date': fields.Date.today() + relativedelta(day=1),
                'end_date': fields.Date.today() + relativedelta(day=1, months=+1, days=-1),
            })
        return res

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

    def print_excel_reports(self):
        filename = 'leave_tracker.xlsx'
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        worksheet = workbook.add_worksheet('Leaves')
        worksheet.set_row(0, 50)
        worksheet.set_column('A:B', 15)
        worksheet.set_column('C:C', 25)
        worksheet.set_column('D:F', 20)
        worksheet.set_column('G:X', 10)
        # worksheet.set_column('M:N', 40)

        heading = workbook.add_format({
            'bold':1,
            'font_size': 15,
            'align': 'center',
            'font_name': 'Times New Roman',
            'text_wrap': True,
            'bg_color': '#D3D3D3'
        })
        data = workbook.add_format({
            'align' : 'center',
            'text_wrap' : True,
        })
        heading_format = workbook.add_format({
                                'align': 'center', 'border': 1,
                                'bold': True, 'size': 25, 'bg_color': '#D3D3D3'})

        row = 0
        col = 0

        worksheet.merge_range('A1:F1', self.company_id.name, heading_format)
        worksheet.freeze_panes(1,1)
        worksheet.freeze_panes(1,2)
        worksheet.freeze_panes(1,3)
        worksheet.freeze_panes(1,4)
        worksheet.freeze_panes(1,5)
        worksheet.freeze_panes(1,6)

        row = 1
        worksheet.set_row(row, 50)
        worksheet.write(row, col,"Plant", heading)
        worksheet.write(row, col+1,"Emp. #", heading)
        worksheet.write(row, col+2,"Employee Name",heading)
        worksheet.write(row, col+3,"Department", heading)
        worksheet.write(row, col+4,"Hire Date", heading)
        worksheet.write(row, col+5,"Termination Date", heading)
        worksheet.write(row, col+6,"LEFT/LEFT EARLY 1", heading)
        worksheet.write(row, col+7,"ABSENT 2", heading)
        worksheet.write(row, col+8,"1/2 DAY REG LOA  3", heading)
        worksheet.write(row, col+9,"REG LOA 4", heading)

        workbook.close()
        result = base64.encodebytes(fp.getvalue())
        fp.close()
        excel_file = self.env['ir.attachment'].create({
            'name': filename,
            'datas': result,
            'res_model': 'leave.tracker.wizard',
            'res_id': self.id,
            'type': 'binary',
        })
        return {
        'type': 'ir.actions.act_url',
        'url': '/web/content/%s?download=true' %  (excel_file.id),
        'target': 'new',
        'nodestroy': False,
        }
