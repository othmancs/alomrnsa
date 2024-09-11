# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ActiveEmployee(models.AbstractModel):
    _name = 'report.saudi_hr.report_active_employee'
    _description = "Active Employee"

    def get_active_employee(self, company_ids):
        emp_list = []
        jobs = self.env['hr.job'].search([])
        for job in jobs:
            employees = self.env['hr.employee'].search([('company_id', '=', company_ids), ('job_id', '=', job.id)])
            job_dict = {'job': job.name, 'no_of_emp': len(employees) or 0, 'req_emp': job.req_emp,
            'company_id': job.company_id.name}
            emp_list.append(job_dict)
        return emp_list

    @api.model
    def _get_report_values(self, doc_ids, data=None):
        if not data.get('id') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        empl = self.get_active_employee(data.get('company_ids'))
        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data,
            'docs': docs,
            'empl': empl
        }
