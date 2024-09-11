# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import _, api, fields, models


class TransferEmployee(models.Model):
    _inherit = 'transfer.employee'

    grade_id = fields.Many2one('hr.grade', 'From Grade', readonly=True)
    new_grade_id = fields.Many2one('hr.grade', 'To Grade')

    @api.onchange('employee_id')
    def onchange_employee(self):
        """
            onchange the value of grade_id based on employee_id
        """
        super(TransferEmployee, self).onchange_employee()
        self.grade_id = self.employee_id.grade_id.id or False


    @api.model_create_multi
    def create(self, vals_list):
        """
            Create new record
            :param values: current record fields data
            :return: Newly created record ID
        """
        for values in vals_list:
            if values.get('employee_id', False):
                employee = self.env['hr.employee'].browse(values['employee_id'])
                values.update({'grade_id': employee.grade_id.id or False})
        return super(HRAppraisalPlan, self).create(vals_list)

    def write(self, values):
        """
            Update an existing record
            :param values: current record fields data
            :return: updated record ID
        """
        if values.get('employee_id', False):
            employee = self.env['hr.employee'].browse(values.get('employee_id'))
            values.update({'grade_id': employee.grade_id.id or False})
        return super(TransferEmployee, self).write(values)

    @api.onchange('new_job_id')
    def onchange_job(self):
        """
            onchange the value of new_grade_id based on new_job_id,
        """
        self.new_grade_id = False

    def get_employee_data(self, employee_id, contract=False):
        """
            Update employee grade based on effective date
        """
        super(TransferEmployee, self).get_employee_data(employee_id, contract)
        if contract:
            employee_id.write({'grade_id': contract.new_grade_id.id or False})
        else:
            employee_id.write({'grade_id': self.new_grade_id.id or False})

    def set_to_draft(self):
        """
            sent the status of generating contract amendment record in draft state
        """
        self.ensure_one()
        super(TransferEmployee, self).set_to_draft()
        self.employee_id.grade_id = self.grade_id.id or False
