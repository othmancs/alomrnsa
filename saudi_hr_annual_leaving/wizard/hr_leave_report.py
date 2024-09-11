# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import xlsxwriter
import base64
from io import BytesIO
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HRLeaveReport(models.TransientModel):
    _name = 'hr.leaves.report'
    _description = 'Leave Report Wizard'

    name = fields.Char("Report Name", default='Leave Report', required=True)
    employee_ids = fields.Many2many('hr.employee', string='Employee')
    holiday_status_ids = fields.Many2many("hr.leave.type", string="Leave Type")
    year_id = fields.Many2one('year.year', string='Year')
    date_start = fields.Date(string='Date Start')
    date_end = fields.Date(string='Date End')

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        for rec in self:
            if rec.date_start > rec.date_end:
                raise ValidationError('Date start must be lower than To Date End.')

    @api.onchange('year_id')
    def onchange_year_id(self):
        self.ensure_one()
        if self.year_id:
            self.date_start = self.year_id.date_start
            self.date_end = self.year_id.date_stop

    def get_data(self):
        self.ensure_one()
        emp_data = []

        employee_ids = self.env['hr.employee'].search([]) if not self.employee_ids else self.employee_ids
        leave_types = self.env['hr.leave.type'].search([]) if not self.holiday_status_ids else self.holiday_status_ids

        for employee in employee_ids:
            leave_list = []

            for leave in leave_types:
                if leave.is_annual_leave:
                    holiday_data = leave.annual_leave_get_days(employee.id, self.date_start, self.date_end)
                else:
                    holiday_data = leave.leave_get_days(employee.id, self.date_start, self.date_end)

                for key, vals in holiday_data.items():
                    leave_type = self.env['hr.leave.type'].browse(key)
                    leave_type_dict = {}
                    leave_type_dict.setdefault(leave_type.name, vals)
                    leave_list.append(leave_type_dict)

            emp_dict = {}
            emp_name = ''
            if employee.name:
                emp_name += employee.name
            if employee.middle_name:
                emp_name += ' '
                emp_name += employee.middle_name
            if employee.last_name:
                emp_name += ' '
                emp_name += employee.last_name
            emp_dict.setdefault(emp_name, leave_list)
            emp_data.append(emp_dict)

        data = {'emp_data': emp_data}
        return data

    def generate_hr_leave_excel_report(self):
        self.ensure_one()
        filename = self.name + '.xlsx'
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        data = {}

        sheet = workbook.add_worksheet("Leave Details")
        heading = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        heading.set_bg_color('#C0C0C0')

        bold = workbook.add_format({'bold': True})
        employee_bold = workbook.add_format({'bold': True})
        employee_bold.set_bg_color('#C0C0C0')
        wrap = workbook.add_format({'text_wrap': 1})
        sheet.set_column(0, 4, 25)
        row = 0

        sheet.merge_range(row, 0, row+1, 4, 'Leave Details', heading)
        row += 3
        sheet.write(row, 0, "Start Date", bold)
        sheet.write(row, 1, self.date_start.strftime('%Y-%m-%d'))
        sheet.write(row, 2, "End Date", bold)
        sheet.write(row, 3, self.date_end.strftime('%Y-%m-%d'))

        row += 2
        sheet.write(row, 0, "Employee", heading)
        sheet.write(row, 1, "Leave Type", heading)
        sheet.write(row, 2, "Allocation Days", heading)
        sheet.write(row, 3, "Leave Days", heading)
        sheet.write(row, 4, "Remaining Leave Days", heading)

        sheet.set_row(row, 45)
        data = self.get_data()
        row += 1
        for emp_data in data.get('emp_data'):
            for emp, leaves in emp_data.items():
                row += 1
                sheet.write(row, 0, emp, bold)
                for leave in leaves:
                    for leave_type, leave_detail in leave.items():
                        row += 1
                        sheet.write(row, 1, leave_type)
                        for key, days in leave_detail.items():
                            if key == 'max_leaves':
                                sheet.write(row, 2, days)
                            if key == 'leaves_taken':
                                sheet.write(row, 3, days)
                            if key == 'remaining_leaves':
                                sheet.write(row, 4, days)

        workbook.close()
        file_save = base64.encodebytes(fp.getvalue())
        fp.close()
        attachment_id = self.env['ir.attachment'].create({'name': filename,
                                                        'datas': file_save,
                                                        'res_model': 'hr.leaves.report',
                                                        'res_id': self.id,
                                                        'type': 'binary',
                                                        })
        return {
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s?download=true' % (attachment_id.id),
                'target': 'new',
                'nodestroy': False,
                }