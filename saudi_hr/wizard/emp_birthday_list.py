# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.tools.misc import format_date as odoo_format_date
from dateutil.relativedelta import relativedelta
from io import BytesIO
import xlsxwriter
import base64


class BirthdayListReports(models.TransientModel):
    _name = "employee.birthday.list"
    _description = "Employee Birthday List Report"

    @api.model
    def default_get(self, default_fields):
        """ Override method for update default values """
        res = super(BirthdayListReports, self).default_get(default_fields)
        res.update({
                'start_date': fields.Date.today() + relativedelta(day=1),
                'end_date': fields.Date.today() + relativedelta(day=1, months=+1, days=-1),
            })
        return res

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)


    def print_pdf_reports(self):
        data = self.read()[0]
        data.update({'start_day': self.start_date.day,
            'end_day': self.end_date.day,
            'start_month': self.start_date.month,
            'end_month': self.end_date.month})
        return self.env.ref('saudi_hr.action_report_birthday_list').report_action(self, data=data)

    def action_view_reports(self):
        start_month = self.start_date.month
        end_month = self.end_date.month
        start_day = self.start_date.day
        end_day = self.end_date.day
        employees = self.env['hr.employee'].search([])
        employees = employees.filtered(lambda l: l.birthday and l.birthday.replace(year=self.start_date.year) >= self.start_date
            and l.birthday.replace(year=self.end_date.year) <= self.end_date)

        tree_view = self.env.ref('saudi_hr.hr_employee_tree_view_inherit')

        return {
            'type': 'ir.actions.act_window',
            'name': _('Employee Birthday'),
            'res_model': 'hr.employee',
            'view_mode': 'from',
            'views': [(tree_view.id, 'tree')],
            'domain': [('id', 'in', employees.ids)],
            'context': self.env.context,
        }

    def print_excel_reports(self):
        filename = 'Birthday_list.xlsx'
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        worksheet = workbook.add_worksheet('All Employees Bday list')
        worksheet.set_row(0, 35)
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:D', 20)
        worksheet.set_column('G:G', 40)

        heading = workbook.add_format({
            'bold':1,
            'font_size' : 15,
            'align' : 'center',
            'font_name' : 'Times New Roman',
            'text_wrap': True
        })

        plant = workbook.add_format({
            'align' : 'center',
        })

        row = 0
        col = 0
        worksheet.write(row, col,"Start Date", heading)
        worksheet.write(row, col+1, str(self.start_date), heading)
        worksheet.write(row, col+2,"End Date", heading)
        worksheet.write(row, col+3, str(self.end_date), heading)
        row += 2

        worksheet.write(row, col,"Emp #", heading)
        worksheet.write(row, col+1,"Hire Date", heading)
        worksheet.write(row, col+2,"Name", heading)
        worksheet.write(row, col+3,"Month", heading)
        worksheet.write(row, col+4,"Day", heading)
        worksheet.write(row, col+5,"Year", heading)
        worksheet.write(row, col+6,"Plant", heading)
        row += 1

        employee_ids = self.env['hr.employee'].search([('birthday', '!=', False)])

        for employee in employee_ids.filtered(lambda l: l.birthday and l.birthday.replace(year=self.start_date.year) >= self.start_date
            and l.birthday.replace(year=self.end_date.year) <= self.end_date):
            worksheet.write(row, col, employee.code or '', plant)
            worksheet.write(row, col+1, employee.date_of_join and str(employee.date_of_join) or '')
            worksheet.write(row, col+2, employee.name)
            worksheet.write(row, col+3, employee.birthday and employee.birthday.strftime("%h") or '',plant)
            worksheet.write(row, col+4, employee.birthday and employee.birthday.day or '',plant)
            worksheet.write(row, col+5, employee.birthday and employee.birthday.year or '',plant)
            worksheet.write(row, col+6, employee.branch_id and employee.branch_id.name or '', plant)
            row += 1

        workbook.close()
        result = base64.encodebytes(fp.getvalue())
        fp.close()
        excel_file = self.env['ir.attachment'].create({
            'name': filename,
            'datas': result,
            'res_model': 'employee.birthday.list',
            'res_id': self.id,
            'type': 'binary',
        })
        return {
        'type': 'ir.actions.act_url',
        'url': '/web/content/%s?download=true' %  (excel_file.id),
        'target': 'new',
        'nodestroy': False,
        }
