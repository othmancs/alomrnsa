# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api, _


class EmployeeBonus(models.Model):
    _inherit = 'employee.bonus'

    grade_id = fields.Many2one('hr.grade', string='Grade', readonly=True)

    @api.onchange('employee_id')
    def onchange_employee(self):
        """
           onchange the value based on selected employee,
           grade
        """
        super(EmployeeBonus, self).onchange_employee()
        self.grade_id = False
        if self.employee_id:
            self.grade_id = self.employee_id.grade_id.id


class EmployeeBonusLines(models.Model):
    _inherit = 'employee.bonus.lines'

    grade_id = fields.Many2one('hr.grade', string='Grade', readonly=True)
    new_grade_id = fields.Many2one('hr.grade', string='To Grade')

    @api.onchange('new_job_id')
    def onchange_new_job(self):
        """
            Based on grade change job
        """
        self.new_grade_id = False
        if self.new_job_id:
            return {'domain': {'new_grade_id': [('hr_job_ids', '=', self.new_job_id.id)]}}
        else:
            return {'domain': {'new_grade_id': []}}

    def get_employee_data(self, line):
        """
            Update employee grade based on effective date
        """
        emp_data = super(EmployeeBonusLines, self).get_employee_data(line)
        grade_dict = {'grade_id': line.new_grade_id.id}
        if line.new_grade_id != line.grade_id:
            emp_data.update(grade_dict)
        return emp_data

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            bonus_id = self.env['employee.bonus'].browse(values.get('employee_bonus_id'))
            if bonus_id:
                values.update({'grade_id': bonus_id.grade_id.id})
        return super(EmployeeBonusLines, self).create(vals_list)

    def write(self, values):
        """
            Update an existing record.
            :param values: updated values
            :return: Current update record ID
        """
        bonus_id = self.env['employee.bonus'].browse(values.get('employee_bonus_id'))
        if bonus_id:
            values.update({'grade_id': bonus_id.grade_id.id})
        return super(EmployeeBonusLines, self).write(values)
