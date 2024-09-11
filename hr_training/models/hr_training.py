# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class TrainingTopic(models.Model):
    _name = 'training.topic'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Training Topic'

    name = fields.Char(string='Name', required=True, tracking=True)
    method_ids = fields.One2many('training.method', 'topic_id', string='Methods', tracking=True)
    date = fields.Date(string='Date', tracking=True)
    review_time_frame = fields.Char(string='Review Time Frame', tracking=True)
    active = fields.Boolean(string='Active', default=True, tracking=True)
    status = fields.Selection([('current', 'Training is Current'), ('not_current', 'Training is not Current')], tracking=True)


class TrainingMethod(models.Model):
    _name = 'training.method'
    _description = 'Training Method'

    name = fields.Char(string='Name', required=True)
    topic_id = fields.Many2one('training.topic', string='Topic')


class HrTraining(models.Model):
    _name = 'hr.training'
    _description = 'HR Training'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order="id desc"

    topic_id = fields.Many2one('training.topic', string='Course', required='True', tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Student Name', tracking=True)
    emp_code = fields.Char(related='employee_id.code', string='Student No.')
    hire_date = fields.Date(related='employee_id.date_of_join', string='Hire Date')
    training_date = fields.Date(string='Training Start Date', tracking=True)
    training_end_date = fields.Date(string='Training End Date', tracking=True)
    is_required = fields.Boolean(string='Required', tracking=True)
    language_id = fields.Many2one('res.lang', string='Prefered Language', tracking=True)
    status = fields.Selection([('not_start', 'Not Start'), ('running', 'Started'), ('trained', 'Trained')],
        default='not_start', required='True', tracking=True)
    notes = fields.Text(string='Notes')

    @api.constrains('hire_date', 'training_date')
    def check_training_date(self):
        for rec in self:
            if rec.employee_id.date_of_join and rec.training_date and rec.employee_id.date_of_join >= rec.training_date:
                raise ValidationError(_('Training start date should not be less than hire date.'))

    def name_get(self):
        result = []
        for training in self:
            name = str(training.employee_id.name or '') + str(training.employee_id.last_name or '')
            if training.topic_id:
                name += ' [' + str(training.topic_id.name) + ']'
            result.append((training.id, name))
        return result

    def training_expire_notification(self):
        today = datetime.now().date()
        for rec in self.search([]):
            if rec.training_end_date:
                before_days = self.env['ir.config_parameter'].sudo().get_param('hr_training.expire_training_notification_days')
                notification_date = rec.training_end_date - relativedelta(days=int(before_days))
                try:
                    template_id = self.env.ref('hr_training.email_template_training_expire')
                except ValueError:
                    template_id = False

                if today == notification_date and template_id:
                    email_to = ''
                    if rec.employee_id.hr_id:
                        email_to = rec.employee_id.hr_id.work_email or ''
                    else:
                        hr = self.env['ir.config_parameter'].sudo().get_param('saudi_hr.hr_id')
                        hr_id = self.env['hr.employee'].browse(int(hr))
                        email_to = hr_id.work_email or ''
                    template_id.with_context(email_to=email_to).send_mail(rec.id, force_send=True)

