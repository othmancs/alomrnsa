# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class HrAppraisal(models.Model):
    _name = 'hr.emp.appraisal'
    _rec_name = 'employee_id'
    _inherit = 'mail.thread'
    _description = 'Appraisal'

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    appraisal_end_date = fields.Date(string="Appraisal Deadline", required=True)
    final_interview = fields.Date(string="Final Interview")
    company_id = fields.Many2one('res.company', string='Company')
    is_manager = fields.Boolean(string="Manager", default=False)
    is_employee = fields.Boolean(string="Employee", default=False)
    hr_collaborator = fields.Boolean(string="Collaborators", default=False)
    hr_colleague = fields.Boolean(string="Colleague", default=False)
    final_evaluation = fields.Html(string='Description')
    appraisal_plan_ids = fields.One2many('hr.emp.appraisal.plan', 'appraisal_id', string="Appraisal Plan")
    total_sent_survey = fields.Integer(string="Count Sent Questions")
    total_complete_survey = fields.Integer(string="Count Answers", compute="_compute_completed_survey")
    total_complete_survey_ratio = fields.Integer(string="Answers", compute="_compute_statistics")
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('sent_mail', 'Sent Mail'), ('done', 'Done'),
                              ('cancel', 'Cancel')], string="Status", default="draft")
    color = fields.Integer(string="color Index")
    job_type = fields.Selection([('ftp', 'Full Time Permanent (FTP)'),
        ('ptp', 'Part Time Permanent (PTP)'),
        ('ptt', 'Part Time Temporary (PTT)'),])
    plant_manager_new_belt_level = fields.Float(string="Plant Manager's Recommended New Wage Level")
    wage_level = fields.Float(string='Wage Level')
    job_level_rating = fields.Float(string='Job Level Rating')
    belt_level_rating = fields.Float(string='Belt Level Rating')
    next_belt_pay_level = fields.Char(string='Promote to next Belt Pay Level')
    date_benefit_commence = fields.Date(string='Date Benefits Commence')
    result = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')], string='Result')


    def _compute_statistics(self):
        """
            Compute statistics of the complete survey ratio
        """
        if self.total_sent_survey > 0:
            self.total_complete_survey_ratio = 100.0 * self.total_complete_survey / self.total_sent_survey
        else:
            self.total_complete_survey_ratio = 0

    def _compute_completed_survey(self):
        """
            Compute the complete survey
        """
        answers = self.env['survey.user_input'].search([('state', '=', 'done'), ('appraisal_id', '=', self.ids[0])])
        self.total_complete_survey = len(answers)

    def fetch_appraisal_reviewer(self):
        """
            get the all appraisal reviewer
        """
        appraisal_reviewers = []
        for appraisal_plan in self.appraisal_plan_ids:
            appraisal_reviewers.append((appraisal_plan, appraisal_plan.employee_ids, appraisal_plan.survey_id))
        return appraisal_reviewers

    def send_mail(self):
        """
            sent an email for appraisal survey form
        """
        send_count = 0
        try:
            template_id = self.env.ref('hr_emp_appraisal.hr_emp_appraisal_email')
        except ValueError:
            template_id = False
        appraisal_reviewers_list = self.fetch_appraisal_reviewer()
        for appraisal_plan, appraisal_reviewers, survey_id in appraisal_reviewers_list:
            for reviewers in appraisal_reviewers:
                url = '%s' % (survey_id.get_start_url())
                response = self.env['survey.user_input'].create({
                                        'survey_id': survey_id.id,
                                        'partner_id': reviewers.user_id.partner_id.id,
                                        'appraisal_id': self.ids[0],
                                        'deadline': self.appraisal_end_date,
                                        'email': reviewers.user_id.email})
                if not reviewers.work_email:
                    raise UserError(_("Please configure %s work email for send mail." % (reviewers.name)))
                if reviewers.work_email and template_id:
                    result = template_id.with_context({'email_to': reviewers, 'url': url}).send_mail(self.id, force_send=False, raise_exception=False)
                    if result:
                        send_count += 1
                        self.total_sent_survey = send_count
                        self.state = 'sent_mail'
                        appraisal_plan.sent_mail = True

    def action_get_answers(self):
        """
            This function will return all the answers posted related to this appraisal.
        """
        tree_res = self.env['ir.model.data']._xmlid_lookup('survey.survey_user_input_view_tree')
        tree_id = tree_res and tree_res[2] or False
        form_res = self.env['ir.model.data']._xmlid_lookup('survey.survey_user_input_view_form')
        form_id = form_res and form_res[2] or False
        return {
            'model': 'ir.actions.act_window',
            'name': 'Answers',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'survey.user_input',
            'views': [(tree_id, 'tree'), (form_id, 'form')],
            'domain': [('state', '=', 'done'), ('appraisal_id', '=', self.ids[0])],
        }

    def action_confirm(self):
        """
            sent the status of generating record in confirm state
        """
        self.state = 'confirm'

    def action_done(self):
        """
            sent the status of generating record in done state
        """
        self.state = 'done'
        contract = self.employee_id.get_current_contracts()
        if contract:
            contract.wage = (self.wage_level * 8) * 30

    def action_cancel(self):
        """
            sent the status of generating record in cancel state
        """
        self.state = 'cancel'

    def action_set_to_draft(self):
        """
            sent the status of generating record in draft state
        """
        self.state = 'draft'

    def check_appraisal_end_date(self):
        """
            sent the appraisal notification and record in done state
        """
        try:
            template_id = self.env.ref('hr_emp_appraisal.hr_emp_appraisal_notification_email')
        except ValueError:
            template_id = False
        for appraisal in self.search([('state', '=', 'sent_mail')]):
            if appraisal.appraisal_end_date:
                notification_date = appraisal.appraisal_end_date - relativedelta(days=2)
                appraisal_reviewers_list = appraisal.fetch_appraisal_reviewer()
                for appraisal_plan, appraisal_reviewers, survey_id in appraisal_reviewers_list:
                    for reviewers in appraisal_reviewers:
                        if fields.Date.today() == notification_date and template_id:
                            template_id.with_context({'email_to': reviewers}).send_mail(appraisal.id, force_send=False, raise_exception=False)
                if fields.Date.today() == appraisal.appraisal_end_date:
                    appraisal.action_done()

    def check_mail_sent(self):
        return True


class HRAppraisalPlan(models.Model):
    _name = 'hr.emp.appraisal.plan'
    _description = 'HR Appraisal Plan'

    fiscalyear_id = fields.Many2one('year.year', 'Fiscal Year', required=True, ondelete='cascade')
    execute_by = fields.Selection([('employee', 'Employee'),
        ('manager', 'Manager'), ('colleague', 'Colleague'),
        ('collaborators', 'Collaborators'), ('hr', 'HR')], string="Execute By", required="True")
    employee_ids = fields.Many2many('hr.employee', string="Employees", required="True")
    survey_id = fields.Many2one('survey.survey', string="Survey", required="True")
    appraisal_id = fields.Many2one('hr.emp.appraisal', string="Appraisal")
    sent_mail = fields.Boolean(string='Sent mail')
    answer_ids = fields.Many2many('survey.user_input', string="Answers")
    color = fields.Integer(string="color Index")

    @api.onchange('execute_by')
    def onchange_execute_by(self):
        """
            onchange the value employee_ids based on selected execute_by
        """
        self.employee_ids = False
        if self.execute_by == 'manager' and self.appraisal_id.employee_id:
            self.employee_ids = [(6, 0, self.appraisal_id.employee_id.parent_id.ids)]
        if self.execute_by == 'employee' and self.appraisal_id.employee_id:
            self.employee_ids = [(6, 0, self.appraisal_id.employee_id.ids)]
        if self.execute_by == 'hr' and self.appraisal_id.employee_id:
            self.employee_ids = [(6, 0, self.appraisal_id.employee_id.hr_id.ids)]


    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get('execute_by') == 'employee' and values.get('appraisal_id'):
                appraisal = self.env['hr.emp.appraisal'].browse(values.get('appraisal_id'))
                values.update({'employee_ids': [(6, 0, appraisal.employee_id.ids)]})
        return super(HRAppraisalPlan, self).create(vals_list)

    def write(self, values):
        """
            Update an existing record.
            :param values: current records fields data
            :return: Current update record ID
        """
        if values.get('execute_by') == 'employee' and values.get('appraisal_id'):
            appraisal = self.env['hr.emp.appraisal'].browse(values.get('appraisal_id'))
            values.update({'employee_ids': [(6, 0, appraisal.employee_id.ids)]})
        return super(HRAppraisalPlan, self).write(values)

    def _return_user(self, employee_ids):
        """
            This method use to Return users
        """
        user_ids = []
        for employee in employee_ids:
            user_ids.append(employee.user_id.id)
        return user_ids

    def action_survey(self):
        """
            If response is available then get this response otherwise get survey form
        """
        if self.env.user.id not in self._return_user(self.employee_ids):
            raise UserError(_("You can't submit your Review."))
        url = self.survey_id.session_link
        answer_done = self.env['survey.user_input'].search([('partner_id', '=', self.env.user.partner_id.id),
                                                            ('appraisal_id', '=', self.appraisal_id.id),
                                                            ('appraisal_plan_id', '=', self.id),
                                                            ('state', '=', 'done')])
        token = answer_done.access_token
        if answer_done:
            return {
                    'type': 'ir.actions.act_url',
                    'name': "Survey",
                    'target': 'self',
                    'url': '/survey/print/%s?answer_token=%s' % (self.survey_id.access_token, token)
                    }
        else:
            response = self.env['survey.user_input'].create({
                                        'survey_id': self.survey_id.id,
                                        'partner_id': self.env.user.partner_id.id,
                                        'appraisal_id': self.appraisal_id.id,
                                        'appraisal_plan_id': self.id,
                                        'employee_id': self.appraisal_id.employee_id.id,
                                        'deadline': self.appraisal_id.appraisal_end_date,
                                        'email': self.env.user.email,
                                        'predefined_question_ids': [(6, 0, self.survey_id.question_and_page_ids.ids)]})
            token = response.access_token
            if token:
                self.answer_ids = [(4, response.id)]
                return {
                    'type': 'ir.actions.act_url',
                    'name': "Survey",
                    'target': 'self',
                    'url': '/survey/start/%s?answer_token=%s' % (self.survey_id.access_token,token)
                }


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    survey_schedule_ids = fields.One2many('survey.schedule', 'employee_id', string='Survey schedule')


class SurveySchedule(models.Model):
    _name = 'survey.schedule'
    _description ='Survey schedule'

    employee_id = fields.Many2one('hr.employee', string='Employee')
    next_evalution = fields.Integer(string='Next Evalution After days')
    evalution_date = fields.Date(string='Evalution Date', compute="calculate_evalution_date", store=True)
    survey_id = fields.Many2one('survey.survey', string='Survey Template')
    evalution_created = fields.Boolean(string='Evalution created?', default=False)

    @api.depends('next_evalution', 'employee_id')
    def calculate_evalution_date(self):
        for rec in self:
            rec.evalution_date = False
            if rec.next_evalution and rec.employee_id and rec.employee_id.date_of_join:
                rec.evalution_date = rec.employee_id.date_of_join + relativedelta(days=int(rec.next_evalution))

    def action_create_evalution(self):
        for rec in self.search([('evalution_created', '=', False), ('evalution_date', '<=', fields.Date.today())]):
            fiscalyear_id = self.env['year.year'].search([('date_start', '<=', rec.evalution_date),
                ('date_stop', '>=', rec.evalution_date)])
            appraisal_plan_vals = [(0, 0, {'fiscalyear_id': fiscalyear_id.id or False,
                'execute_by': 'employee', 'survey_id': rec.survey_id.id}),
            (0, 0, {'fiscalyear_id': fiscalyear_id.id or False,
                'execute_by': 'manager',
                'employee_ids': [(6, 0, rec.employee_id.parent_id.ids or [])],
                'survey_id': rec.survey_id.id}),
            (0, 0, {'fiscalyear_id': fiscalyear_id.id or False,
                'execute_by': 'hr',
                'employee_ids': [(6, 0, rec.employee_id.hr_id.ids or [])],
                'survey_id': rec.survey_id.id})]
            survey_vals = {'employee_id': rec.employee_id.id,
                            'appraisal_end_date': rec.evalution_date,
                            'appraisal_plan_ids': appraisal_plan_vals or []}
            self.env['hr.emp.appraisal'].create(survey_vals)
            rec.evalution_created = True

