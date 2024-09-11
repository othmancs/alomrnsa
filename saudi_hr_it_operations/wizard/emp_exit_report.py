# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from io import BytesIO
import xlsxwriter
import base64
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class EmpExitReport(models.AbstractModel):
    _name = 'report.saudi_hr_it_operations.report_emp_exit'
    _description = "Emp Exit Report"

    @api.model
    def _get_report_values(self, doc_ids, data=None):
        if not data.get('id') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        # employees = self.env['hr.employee'].search([('birthday', '!=', False)]).filtered(lambda l: l.birthday.month >= int(data['start_month']) and
        #     l.birthday.month <= int(data['end_month']) and l.birthday.day >= int(data['start_day']) and l.birthday.day <= int(data['end_day']))
        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data,
            'docs': docs,
            # 'employees': employees,
        }



class EmpExitWizard(models.TransientModel):
    _name = 'emp.exit.wizard'
    _description = 'Employee Exit Wizard'

    @api.model
    def default_get(self, fields_list):
        """
            Override method for get default values
        """
        res = super(EmpExitWizard, self).default_get(fields_list)
        current_date = fields.Date.today()
        res.update({
                'start_date': current_date + relativedelta(day=1),
                'end_date': current_date + relativedelta(day=1, months=+1, days=-1),
            })
        return res

    start_date = fields.Date(string='Start Date', default=fields.Date.today(), required=True)
    end_date = fields.Date(string='End Date', default=fields.Date.today(), required=True)

    _sql_constraints = [
        ('date_check', "CHECK((start_date <= end_date))", "Please enter valid date")
    ]

    def print_pdf_reports(self):
        data = self.read()[0]
        return self.env.ref('saudi_hr_it_operations.action_report_emp_exit').report_action(self, data=data)

    def action_view_reports(self):
        exit_records = self.get_exit_records().mapped('employee_id')
        tree_view = self.env.ref('saudi_hr.hr_employee_tree_view_inherit')
        if exit_records:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Employee Exit'),
                'res_model': 'hr.employee',
                'view_mode': 'from',
                'views': [(tree_view.id, 'tree')],
                'domain': [('id', 'in', exit_records.ids)],
                'context': self.env.context,
            }
        else:
            raise ValidationError(_('No Record Found!'))

    def get_exit_records(self):
        exit_ids = self.env['emp.exit.procedure'].search([('last_date', '>=', self.start_date), ('last_date', '<=', self.end_date)])
        return exit_ids

    def get_reg_rate(self, employee):
        contract = employee.get_current_contracts()
        rate = 0.0
        if contract and contract.wage:
            hours_per_day = contract.resource_calendar_id.hours_per_day or 8
            rate = (contract.wage / 30) / hours_per_day
        return rate

    def print_excel_reports(self):
        filename = 'Employee_Exit_Report.xlsx'
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        worksheet = workbook.add_worksheet('Exit Employee')
        worksheet.set_row(0, 35)
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:K', 20)
        worksheet.set_column('L:L', 40)

        heading = workbook.add_format({
            'bold':1,
            'font_size' : 15,
            'align' : 'center',
            'font_name' : 'Times New Roman',
            'text_wrap': True,
            'bg_color': '#D3D3D3'
        })

        heading_date = workbook.add_format({
            'bold':1,
            'font_size' : 15,
            'align' : 'center',
            'font_name' : 'Times New Roman',
            'text_wrap': True,
        })

        heading_format = workbook.add_format({
                                'align': 'center', 'border': 1,
                                'bold': True, 'size': 25, 'bg_color': '#D3D3D3'})

        data = workbook.add_format({
            'align' : 'center',
            'text_wrap' : True,
        })

        row = 0
        col = 0
        worksheet.merge_range('A1:L1', "Employee Exit Report", heading_format)
        row += 2
        worksheet.write(row, col,"Start Date", heading_date)
        worksheet.write(row, col+1, str(self.start_date), heading_date)
        worksheet.write(row, col+3,"End Date", heading_date)
        worksheet.write(row, col+4, str(self.end_date), heading_date)
        row += 2

        worksheet.write(row, col,"Team #", heading)
        worksheet.write(row, col+1,"First Name", heading)
        worksheet.write(row, col+2,"Plant", heading)
        worksheet.write(row, col+3,"Job Title", heading)
        worksheet.write(row, col+4,"Status", heading)
        worksheet.write(row, col+5,"Contact Name", heading)
        # worksheet.write(row, col+6,"Contact#", heading)
        worksheet.write(row, col+6,"Last Day Worked", heading)
        # worksheet.write(row, col+8,"Address", heading)
        # worksheet.write(row, col+9,"City", heading)
        # worksheet.write(row, col+10,"Province", heading)
        # worksheet.write(row, col+11,"Postal Code", heading)
        # worksheet.write(row, col+12,"Birthdate", heading)
        worksheet.write(row, col+7,"Telephone", heading)
        worksheet.write(row, col+8,"Hire Date", heading)
        worksheet.write(row, col+9,"Reg. Rate ", heading)
        worksheet.write(row, col+10,"Rehire", heading)
        worksheet.write(row, col+11,"Notes", heading)
        row += 1

        for rec in self.get_exit_records():
            emp = rec.employee_id
            rate = self.get_reg_rate(rec.employee_id)
            worksheet.write(row, col, emp.code or '', data)
            worksheet.write(row, col+1, emp.name or '')
            worksheet.write(row, col+2, emp.branch_id.name or '', data)
            worksheet.write(row, col+3, emp.job_id.name or '', data)
            worksheet.write(row, col+4, rec.exit_type.name or '', data)
            worksheet.write(row, col+5, emp.address_home_id.name or '', data)
            # worksheet.write(row, col+6, emp.address_home_id.mobile or '', data)
            worksheet.write(row, col+6, emp.date_of_leave and str(emp.date_of_leave) or '', data)
            # worksheet.write(row, col+8, emp.address_home_id.street or '', data)
            # worksheet.write(row, col+9, emp.address_home_id.city or '', data)
            # worksheet.write(row, col+10, emp.address_home_id.state_id.name or '',data)
            # worksheet.write(row, col+11, emp.address_home_id.zip or '', data)
            # worksheet.write(row, col+12, emp.birthday and str(emp.birthday) or '', data)
            worksheet.write(row, col+7, emp.phone or '', data)
            worksheet.write(row, col+8, emp.date_of_join and str(emp.date_of_join) or '', data)
            worksheet.write(row, col+9, "%.2f"% (rate), data)
            worksheet.write(row, col+10, rec.rehire and 'Yes' or 'NO', data)
            worksheet.write(row, col+11, rec.hr_notes or '', data)
            row += 1

        workbook.close()
        result = base64.encodebytes(fp.getvalue())
        fp.close()
        excel_file = self.env['ir.attachment'].create({
            'name': filename,
            'datas': result,
            'res_model': 'emp.exit.wizard',
            'res_id': self.id,
            'type': 'binary',
        })
        return {
        'type': 'ir.actions.act_url',
        'url': '/web/content/%s?download=true' %  (excel_file.id),
        'target': 'new',
        'nodestroy': False,
        }
