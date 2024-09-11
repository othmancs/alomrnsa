# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.tools.misc import format_date as odoo_format_date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from io import BytesIO
import xlsxwriter
import base64


class EmployeeReports(models.TransientModel):
    _name = "employee.head.count"
    _description = "Employee Head Count Report"

    based_on = fields.Selection([('Department', 'Department'), ('Job', 'Job'), ('Manager', 'Manager')],
                                string='Based on')
    department_ids = fields.Many2many('hr.department', string='Department')
    job_ids = fields.Many2many('hr.job', string='Job')
    manager_ids = fields.Many2many('hr.employee', string='Manager')
    branch_ids = fields.Many2many('hr.branch', string='Locations')
    # ('active', 'Employment/Active'),
    #                                     ('inactive', 'Inactive'),
    #                                     ('long_term_secondment', 'Long Term Secondment'),
    #                                     ('probation', 'Probation'),
    #                                     ('notice_period', 'Notice Period'),
    #                                     ('terminate', 'Terminated/Inactive')
    employee_status = fields.Selection([('hired', 'Hired'),
                                        ('layoff', 'Layoff'),
                                        ('terminated', 'Terminated'),
                                        ('quit', 'Quit'),
                                        ('loa', 'LOA')
                                        ], string='Employment Status', default='hired')

    def print_reports(self):
        self.ensure_one()
        return self.env.ref('saudi_hr.action_report_hr_employee').report_action(self)

    @api.onchange('based_on')
    def onchange_based_on(self):
        self.department_ids = False
        self.job_ids = False
        self.manager_ids = False

    def get_dept(self):
        data = []
        if self.based_on == 'Department':
            department_domain = [('id', 'in', self.department_ids.ids)] if self.department_ids else []
            departments = self.env['hr.department'].search(department_domain)
            for department in departments:
                data.append(department.name)
        if self.based_on == 'Job':
            job_domain = [('id', 'in', self.job_ids.ids)] if self.job_ids else []
            jobs = self.env['hr.job'].search(job_domain)
            for job in jobs:
                data.append(job.name)
        if self.based_on == 'Manager':
            manager_domain = [('id', 'in', self.manager_ids.ids)] if self.manager_ids else [('manager', '=', True)]
            managers = self.env['hr.employee'].search(manager_domain)
            for manager in managers:
                data.append(manager.name)
        return data

    def get_emp(self, data_id):
        emp = []
        if self.based_on == 'Department':
            dep = self.env['hr.department'].search([('name', '=', data_id)])
            employee = self.env['hr.employee'].search([('department_id', '=', dep.id)])
        if self.based_on == 'Job':
            job = self.env['hr.job'].search([('name', '=', data_id)])
            employee = self.env['hr.employee'].search([('job_id', '=', job.id)])
        if self.based_on == 'Manager':
            manager = self.env['hr.employee'].search([('name', '=', data_id)])
            employee = self.env['hr.employee'].search([('parent_id', '=', manager.id)])
        if self.employee_status and employee:
            employee = employee.filtered(lambda l: l.employee_status == self.employee_status)
        if self.branch_ids and employee:
            employee = employee.filtered(lambda l: l.branch_id.id in self.branch_ids.ids)

        for rec in employee:
            emp_dict = {'code': rec.code,
                        'name': rec.name,
                        'joining_date': odoo_format_date(self.env, rec.date_of_join),
                        'location': rec.branch_id.name,
                        'status': dict(rec._fields['employee_status'].selection).get(rec.employee_status)}
            emp.append(emp_dict)
        return emp

    def total_emp(self, data_id):
        print("==data_id==", data_id)
        employees = self.get_emp(data_id)
        return len(employees)

    def action_view_reports(self):
        context = dict(self.env.context) or {}
        tree_view = self.env.ref('saudi_hr.hr_employee_tree_view_inherit')
        domain = []
        if self.based_on == 'Department':
            context.update({'search_default_group_department':1})
            if self.department_ids:
                domain = [('department_id', 'in', self.department_ids.ids)]
        if self.based_on == 'Job':
            if self.job_ids:
                domain = [('job_id', '=', self.job_ids.ids)]
            context.update({'search_default_group_job':1})
        if self.based_on == 'Manager':
            if self.manager_ids:
                domain = [('parent_id', '=', self.manager_ids.ids)]
            context.update({'search_default_group_manager':1})

        employee = self.env['hr.employee'].search(domain)

        if self.employee_status and employee:
            employee = employee.filtered(lambda l: l.employee_status == self.employee_status)
        if self.branch_ids and employee:
           employee = employee.filtered(lambda l: l.branch_id.id in self.branch_ids.ids)

        if employee:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Employee '),
                'res_model': 'hr.employee',
                'view_mode': 'from',
                'views': [(tree_view.id, 'tree')],
                'domain': [('id', 'in', employee.ids)],
                'context': context,
            }
        else:
            raise UserError(_('Record Not Found!'))

    def print_excel_reports(self):
        filename = 'Employee_Head_count.xlsx'
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        worksheet = workbook.add_worksheet('Employees')
        worksheet.set_row(0, 35)
        worksheet.set_column('A:E', 20)
        heading = workbook.add_format({
            'bold':1,
            'font_size' : 15,
            'align' : 'center',
            'font_name' : 'Times New Roman',
            'text_wrap': True
        })
        heading_format = workbook.add_format({
                                'align': 'center', 'border': 1,
                                'bold': True, 'size': 25, 'bg_color': '#D3D3D3'})
        data = workbook.add_format({
            'align' : 'center',
        })
        row = 0
        col = 0
        worksheet.merge_range('A1:E1', ("%s wise Employees" % self.based_on), heading_format)
        row += 2

        for rec in self.get_dept():
            worksheet.set_row(row, 25)
            worksheet.merge_range('A%s:E%s' % (row+1, row+1), "%s: %s" % (self.based_on, rec), heading)
            row += 1
            worksheet.write(row, col,"Code", heading)
            worksheet.write(row, col+1,"Name", heading)
            worksheet.write(row, col+2,"Joining Date", heading)
            worksheet.write(row, col+3,"Location", heading)
            worksheet.write(row, col+4,"Status", heading)
            row += 1
            for emp in self.get_emp(rec):
                worksheet.write(row, col,emp.get('code') or '')
                worksheet.write(row, col+1, emp.get('name') or '')
                worksheet.write(row, col+2, emp.get('joining_date') or '')
                worksheet.write(row, col+3, emp.get('location') or '')
                worksheet.write(row, col+4, emp.get('status'))
                row += 1
            row += 2

        workbook.close()
        result = base64.encodebytes(fp.getvalue())
        fp.close()
        excel_file = self.env['ir.attachment'].create({
            'name': filename,
            'datas': result,
            'res_model': 'employee.head.count',
            'res_id': self.id,
            'type': 'binary',
        })
        return {
        'type': 'ir.actions.act_url',
        'url': '/web/content/%s?download=true' %  (excel_file.id),
        'target': 'new',
        'nodestroy': False,
        }
