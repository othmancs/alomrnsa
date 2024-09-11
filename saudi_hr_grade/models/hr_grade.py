# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api, _


class HrGrade(models.Model):
    _name = 'hr.grade'
    _description = "Grade Description"

    name = fields.Char('Name', required=True)
    hr_job_ids = fields.One2many('hr.job', 'grade_id', 'Job')
    is_above_manager = fields.Boolean('Is Above Manager', help="Tick this if grade is above manager level.")


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    grade_id = fields.Many2one('hr.grade', 'Grade')

    @api.onchange('job_id')
    def onchange_job_id(self):
        """
            Based on job change grade
        """
        self.grade_id = False
        if self.job_id:
            return {'domain': {'grade_id': [('id', 'in', self.job_id.grade_id.ids)]}}
        else:
            return {'domain':{'grade_id': []}}


class HrJob(models.Model):
    _inherit = 'hr.job'
    _description = 'HR Job'

    grade_id = fields.Many2one('hr.grade', string='Grade')
