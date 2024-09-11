# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Employee(models.Model):
    _inherit = "hr.employee"

    advance_salary_count = fields.Integer(compute='_compute_advance_salary_count', string='Advance Salary Count')

    def _compute_advance_salary_count(self):
        for rec in self:
            rec.advance_salary_count = self.env['hr.advance.salary'].search_count([('employee_id', '=', rec.id)])

    @api.model
    def get_employee(self):
        """
            Get Employee record depends on current user.
        """
        employee_ids = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        return employee_ids[0] if employee_ids else False


class HrJob(models.Model):
    _inherit = 'hr.job'

    advance_salary_limit = fields.Float('Advance Salary Limit (%)', default=50.0)

    @api.onchange('advance_salary_limit')
    def onchange_advance_salary_limit(self):
        if self.advance_salary_limit < 0 or self.advance_salary_limit > 100:
            raise ValidationError(_("Advance salary limit Range 0 to 100%."))
