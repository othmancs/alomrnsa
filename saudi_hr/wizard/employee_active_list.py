# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models, _
from io import BytesIO
import xlsxwriter
import base64


class EmployeeActiveList(models.TransientModel):
    _name = 'employee.active.list.reports'
    _description = 'Employee Active List'

    job_ids = fields.Many2many('hr.job', string="Job Position")
    company_ids = fields.Many2many('res.company', string='Company')

    @api.model
    def default_get(self, default_fields):
        """ set default value
        """
        res = super(EmployeeActiveList, self).default_get(default_fields)
        context = dict(self.env.context) or {}
        company_ids = context.get('allowed_company_ids') or []
        jobs = self.env['hr.job'].search([('company_id', 'in', company_ids)])
        job_ids = jobs.ids or []
        res['company_ids'] = [(6, 0, company_ids)]
        res['job_ids'] = [(6, 0, job_ids)]
        return res

    @api.onchange('company_ids')
    def get_job(self):
        if self.company_ids:
            job_ids = self.env['hr.job'].search([('company_id', 'in', self.company_ids.ids)])
            self.job_ids = [(6, 0, job_ids.ids)]

    def get_active_employee(self):
        emp_list = []
        jobs = self.env['hr.job'].search([])
        for job in jobs:
            employees = self.env['hr.employee'].search([('company_id', 'in', self.company_ids.ids), ('job_id', '=', job.id), ('active', '=', True)])
            job_dict = {'job': job.name, 'no_of_emp': len(employees) or 0, 'req_emp': job.req_emp,
                'company_id': job.company_id.name}
            emp_list.append(job_dict)
        return emp_list

    def generate_employee_active_list_excel_report(self):
        filename = 'EmployeeActiveList.xlsx'
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        worksheet = workbook.add_worksheet('Employee Active List')
        worksheet.set_column('A:A', 40)
        worksheet.set_column('C:Z', 10)

        heading = workbook.add_format({
            'bold':1,
            'font_size' : 15,
            'align' : 'center',
            'font_name' : 'Calibri',
            'text_wrap': True,
            'border': 2,
            
        })
        head_content = workbook.add_format({
            'bold':1,
            'font_size' : 12,
            'align' : 'center',
            'font_name' : 'Calibri',
            'text_wrap': True,
            'border': 2,
        })
        total_content = workbook.add_format({
            'font_size' : 12,
            'align' : 'center',
            'font_name' : 'Calibri',
            'text_wrap': True
        })
        content = workbook.add_format({
            'bold':1,
            'font_size' : 12,
            'font_name' : 'Calibri',
            'text_wrap': True
        })
        red = workbook.add_format({
            'bg_color': 'red',
            'align':'center'
            })
        yellow = workbook.add_format({
            'bg_color': 'yellow',
            'align':'center'
            })
        green = workbook.add_format({
            'bg_color': 'green',
            'align':'center'
            })

        col = 0
        row = 1
        worksheet.merge_range(row, 0, row+1, 6, 'Employee Active List', heading)
        row = 4
        worksheet.merge_range('A%s:A%s' % (col+5, col+6), '', head_content)
        for company in self.company_ids:

            worksheet.merge_range(row, col+1, row, col+3, company.name, head_content)
            worksheet.set_column(col+3, 5)

            worksheet.write(row+1, col+1,"Actual", head_content)
            worksheet.write(row+1, col+2,"Required", head_content)
            worksheet.write(row+1, col+3,"+/-", head_content)
            col += 3

        col = 0
        row = 8
        total_employee = 0

        job_emp_details = self.get_active_employee()

        for job in self.job_ids:
            worksheet.write(row, col, job.name, content)
            row +=1
            worksheet.write(row, col, "TOTALS EE'S AT EACH SHOP", content)

        for company in self.company_ids:
            total_actual_emp = 0
            total_req_emp = 0
            total_emps = 0
            row=8
            for job in self.job_ids:
                if job_emp_details:
                    for job_dict in job_emp_details:

                        if company.name == job_dict.get('company_id') and job.name == job_dict.get('job'):
                            total_employee = job_dict.get('no_of_emp') or 0
                            req_emp = job_dict.get('req_emp')

                            worksheet.write(row, col+1, total_employee, total_content)
                            worksheet.write(row, col+2, req_emp, total_content)
                            total = total_employee - req_emp

                            if total_employee > req_emp:
                                worksheet.write(row, col+3, total, yellow)
                            if total_employee < req_emp:
                                worksheet.write(row, col+3, total, red)
                            if total_employee == req_emp:
                                worksheet.write(row, col+3, total, green)

                            total_actual_emp += total_employee
                            total_req_emp += req_emp
                            total_emps += total

                row += 1
            worksheet.write(row, col+1, total_actual_emp, total_content)
            worksheet.write(row, col+2, total_req_emp, total_content)
            worksheet.write(row, col+3, total_emps, total_content)
            col+=3

        workbook.close()
        result = base64.encodebytes(fp.getvalue())
        fp.close()
        excel_file = self.env['ir.attachment'].create({
            'name': filename,
            'datas': result,
            'res_model': 'employee.active.list.reports',
            'res_id': self.id,
            'type': 'binary',
        })
        return {
        'type': 'ir.actions.act_url',
        'url': '/web/content/%s?download=true' %  (excel_file.id),
        'target': 'new',
        'nodestroy': False,
        }

    def generate_employee_active_list_pdf_report(self):
        data = self.read()[0]
        return self.env.ref('saudi_hr.action_report_employee_active').report_action(self, data=data)


class EmployeeActiveListView(models.Model):
    _name = 'employee.active.list.view'
    _description = 'Employee Active List View'
    _auto = False

    job_id = fields.Many2one('hr.job', string='Job')
    company_id = fields.Many2one('res.company', string='Company')
    actual_emp = fields.Integer(string='Actual')
    required_emp = fields.Integer(string='Required')
    diff = fields.Integer(string='+/-')

    def _select(self, fields=None):
        if not fields:
            fields = {}
        select_ = """
        row_number() OVER() AS id,
        j.id AS job_id,
        j.company_id AS company_id,
        count(*) AS actual_emp,
        j.req_emp AS required_emp,
        (j.req_emp - count(*)) AS diff
        """

        for field in fields.values():
            select_ += field
        return select_

    def _from(self, from_clause=''):
        from_ = """
            hr_job j LEFT JOIN hr_employee e ON e.job_id = j.id
            %s
        """ % from_clause
        return from_

    def _group_by(self, groupby=''):
        groupby_ = """
            j.id, j.company_id %s
        """ % (groupby)
        return groupby_

    def _query(self, with_clause='', fields=None, groupby='', from_clause=''):
        if not fields:
            fields = {}
        with_ = ("WITH %s" % with_clause) if with_clause else ""
        query =  '%s (SELECT %s FROM %s where j.id IS NOT NULL GROUP BY %s)' % \
               (with_, self._select(fields), self._from(from_clause), self._group_by(groupby))
        return query

    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))
