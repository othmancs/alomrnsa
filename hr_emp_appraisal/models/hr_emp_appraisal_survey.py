# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class SurveyInput(models.Model):
    _inherit = 'survey.user_input'

    appraisal_id = fields.Many2one('hr.emp.appraisal', string="Appriasal id")
    appraisal_plan_id = fields.Many2one('hr.emp.appraisal.plan', string="Appriasal Plan")
    employee_id = fields.Many2one('hr.employee', string='Employee')
    emp_code = fields.Char(related='employee_id.code', string='Code')
    emp_joining_date = fields.Date(related='employee_id.date_of_join', string='Hire Date')
    emp_sign = fields.Char(related='employee_id.name', string='Signature')
    score = fields.Float(string='Score', compute="calculate_job_skill_belt_level")
    job_skill_belt_level = fields.Float(string='Job Skill Belt Level', compute="calculate_job_skill_belt_level")
    belt_level = fields.Float(string='Belt Level', compute="calculate_job_skill_belt_level")

    def calculate_job_skill_belt_level(self):
        for rec in self:
            rec.job_skill_belt_level = 0.0
            rec.belt_level = 0.0
            no_of_line = len(rec.user_input_line_ids)
            rec.score = sum(rec.user_input_line_ids.mapped('value_numerical_box'))
            job_skill_score = sum(rec.user_input_line_ids.filtered(lambda l: l.is_job_skill).mapped('value_numerical_box'))
            if no_of_line:
                rec.job_skill_belt_level = job_skill_score/no_of_line
                rec.belt_level = rec.score/no_of_line


class SurveyQuestion(models.Model):
    _inherit = 'survey.question'

    is_job_skill = fields.Boolean(string='Job Skill')
    user_ids = fields.Many2many('res.users', string='Users')


class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input.line'

    is_job_skill = fields.Boolean(related='question_id.is_job_skill', string='Job Skill')


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def action_survey_user_input_completed(self):
        action = self.env['ir.actions.act_window']._for_xml_id('survey.action_survey_user_input')
        # ctx = dict(self.env.context)
        # ctx.update({'search_default_employee_id': self.ids})
        # action['context'] = ctx
        action['domain'] = ['|', ('employee_id', '=', self.id), ('appraisal_id.employee_id', '=', self.id)]
        return action

class SurveySurvey(models.Model):
    _inherit = 'survey.survey'

    def _get_survey_questions(self, answer=None, page_id=None, question_id=None):
        questions, page_or_question_id = super(SurveySurvey, self)._get_survey_questions(answer, page_id, question_id)
        questions = questions.filtered(lambda l: not l.user_ids or self.env.user.id in l.user_ids.ids)
        return questions, page_or_question_id
