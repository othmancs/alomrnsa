# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

_states = [('draft', 'Draft'), ('confirm', 'Waiting Approval'), ('approve', 'Approved'), ('done', 'Done'), ('refuse', 'Refused')]


class EmployeeProbationReview(models.Model):
    _name = 'emp.probation.review'
    _description = 'Employee Probation Review'
    _order = 'id desc'
    _inherit = ['mail.thread']

    @api.depends('join_date', 'extend_end_date', 'employment_status')
    def compute_date(self):
        """
            set probation complete date and extend date
        """
        probation_duration = self.env['ir.config_parameter'].sudo().get_param('saudi_hr_probation.probation_duration') or 3
        for rec in self:
            if rec.join_date:
                rec.probation_complete_date = rec.join_date + relativedelta(months=rec.employee_id.department_id and rec.employee_id.department_id.probation_duration or probation_duration)
            if rec.extend_end_date:
                rec.probation_complete_date = rec.extend_end_date

    # Fields Employee Probation Review
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    job_id = fields.Many2one('hr.job', readonly=True, string='Job Position')
    branch_id = fields.Many2one('hr.branch', 'Office', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id, required=True)
    # contract_id = fields.Many2one('hr.contract', string='Contract', required=True)
    department_id = fields.Many2one('hr.department', readonly=True, string='Department')
    line_manager_id = fields.Many2one('hr.employee', string='Manager', required=True, readonly=True)
    hof_id = fields.Many2one('hr.employee', string='Head of Department', readonly=True)
    join_date = fields.Date(string='Join Date', readonly=True, required=True)
    extend_start_date = fields.Date(string='Extend Start Date')
    extend_end_date = fields.Date(string='Extend End Date')
    probation_complete_date = fields.Date(string='Probation Complete Date', compute='compute_date', store=True, readonly=True)
    probation_plan = fields.Html(string='Probation Plan', required=True)
    review = fields.Html(string='Review')
    approved_date = fields.Datetime(string='Approved Date', readonly=True, copy=False)
    approved_by = fields.Many2one('res.users', string='Approved by', readonly=True, copy=False)
    state = fields.Selection(_states, string='Status', default='draft', tracking=True)
    employment_status = fields.Selection([('end', 'Probation End'),
                                          ('relieve', 'Relieve'),
                                          ('extend', 'Extend Probation')], 'Employment Status')
    rating = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'),
                               ('8', '8'), ('9', '9'), ('10', '10')], string="Progress Rate", index=True)

    def send_probation_mail(self):
        """
            This function send mail to employee about his/her probation status
        """
        self.ensure_one()
        try:
            if self.employment_status == 'extend':
                template_id = self.env.ref('saudi_hr_probation.email_template_probation_extend')
            elif self.employment_status == 'end':
                template_id = self.env.ref('saudi_hr_probation.email_template_probation_end')
            else:
                template_id = self.env.ref('saudi_hr_probation.email_template_employee_relieving')
        except ValueError:
            template_id = False
        if template_id:
            template_id.send_mail(self.id, force_send=True)

    @api.onchange('employment_status')
    def onchange_employment_status(self):
        """
            Onchange the value extend_start_date based on selected employment_status
        """
        self.extend_end_date = False
        extend_start_date = datetime.today().date() + relativedelta(days=1)
        if self.employment_status == 'extend':
            self.extend_start_date = extend_start_date

    @api.onchange('employee_id')
    def onchange_employee(self):
        """
            Onchange the value based on selected employee,
            Hof, manager, job, department, company, join date, contract
        """
        self.hof_id = False
        self.line_manager_id = False
        self.job_id = False
        self.department_id = False
        self.join_date = False
        # self.contract_id = False
        self.branch_id = False
        self.employment_status = False
        if self.employee_id:
            self.hof_id = self.employee_id.coach_id.id  # self.employee_id.parent_id.id
            self.line_manager_id = self.employee_id.parent_id.id  # self.employee_id.coach_id.id
            self.job_id = self.employee_id.job_id.id
            self.branch_id = self.employee_id.branch_id.id or False
            self.department_id = self.employee_id.department_id.id
            self.company_id = self.employee_id.company_id.id
            self.join_date = self.employee_id.date_of_join
            # self.contract_id = self.employee_id.contract_id.id

    def unlink(self):
        """
            To remove the record, which is not in 'confirm', 'approve', 'done', 'refuse' states
        """
        for record in self:
            if record.state in ['confirm', 'approve', 'done', 'refuse']:
                raise UserError(_('You cannot remove the record which is in %s state!') % record.state)
        return super(EmployeeProbationReview, self).unlink()

    def name_get(self):
        """
            to use retrieving the employee name
        """
        result = []
        for review in self:
            name = review.employee_id.name or ''
            result.append((review.id, name))
        return result

    def review_confirm(self):
        """
            sent the status of his/her probation in confirm state
        """
        self.ensure_one()
        if self.employee_id and self.employee_id.parent_id and self.employee_id.parent_id.user_id:
            self.message_subscribe(partner_ids=self.employee_id.parent_id.user_id.partner_id.ids)
        self.message_post(message_type="email", subtype_xmlid='mail.mt_comment', body="Employee Probation Review Request Confirmed.")
        self.state = 'confirm'

    def review_done(self):
        """
            sent the status of his/her probation in done state
        """
        self.ensure_one()
        date = self.probation_complete_date - timedelta(days=10)
        today_date = date.today()
        if today_date >= date and today_date <= self.probation_complete_date:
            self.state = 'done'
            if self.employment_status == 'end':
                self.employee_id.employee_status = 'hired'
        else:
            raise ValidationError(_("Today's date must be 10 days less then Probation Complete Date"))

    def review_approve(self):
        """
            sent the status of his/her probation in approve state
        """
        self.ensure_one()
        self.write({'state': 'approve',
                    'approved_by': self.env.uid,
                    'approved_date': datetime.today()
                    })
        self.message_post(message_type="email", subtype_xmlid='mail.mt_comment',
                          body="Employee Probation Review Request Approved.")

    def review_refuse(self):
        """
            sent the status of his/her probation in refuse state
        """
        self.ensure_one()
        self.state = 'refuse'
        self.message_post(message_type="email", subtype_xmlid='mail.mt_comment',
                          body="Employee Probation Review Request Refused.")

    def set_draft(self):
        """
            sent the status of his/her probation in draft state
        """
        self.ensure_one()
        self.write({'state': 'draft',
                    'approved_by': False,
                    'approved_date': False,
                    'employment_status': False,
                    'extend_end_date': False
                    })
        self.message_post(message_type="email", subtype_xmlid='mail.mt_comment',
                          body="Employee Probation Review Request Created.")

    def run_scheduler(self):
        """
            cron job for automatically done probation
        """
        for probation in self.search([('state', '=', 'approve')]):
            if fields.Date.today() == probation.probation_complete_date and probation.employment_status:
                probation.state = 'done'
                if probation.employment_status == 'end':
                    probation.employee_id.employee_status = 'hired'
