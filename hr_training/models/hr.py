# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    training_ids = fields.One2many('hr.training', 'employee_id', string='Training')
    country_code = fields.Char(related='country_id.code', string='Country Code')

    @api.onchange('job_id')
    def onchange_department(self):
        if self.job_id and self.job_id.training_topic_ids:
            training_list = []
            for topic in self.job_id.training_topic_ids:
                training_vals = {'employee_id': self.id,
                    'topic_id': topic.id,
                    'is_required': True,
                    'status': 'not_start',
                    }
                training_list.append((0, 0, training_vals))
            self.training_ids = training_list

class HrDepartment(models.Model):
    _inherit = 'hr.department'

    training_topic_ids = fields.Many2many('training.topic', 'department_training_rel', string='Training Package', help='Required Training for this department.')


class HrJob(models.Model):
    _inherit = 'hr.job'

    training_topic_ids = fields.Many2many('training.topic', 'job_training_rel', string='Required Trainings')

    @api.onchange('department_id')
    def onchange_department(self):
        self.training_topic_ids = [(5, )]
        if self.department_id and self.department_id.training_topic_ids:
            self.training_topic_ids = [(6, 0, self.department_id.training_topic_ids.ids)]
