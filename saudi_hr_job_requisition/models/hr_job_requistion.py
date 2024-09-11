# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class HRJobRequisition(models.Model):
    _name = 'hr.job.requisition'
    _inherit = ['mail.thread']
    _description = 'HR Job Requisition'
    _order = 'id desc'

    @api.depends('no_of_recruitment')
    def _no_of_employee(self):
        """
            this function is used to calculate number of employee
        """
        for rec in self:
            if rec.no_of_recruitment and rec.job_id:
                rec.job_id.no_of_recruitment = rec.no_of_recruitment
                hr_emp_obj = self.env['hr.employee'].search([('job_id', '=', rec.job_id.id)])
                rec.no_of_employee = len(hr_emp_obj)
                rec.expected_employees = len(hr_emp_obj) + rec.no_of_recruitment

    @api.depends('no_of_employee', 'no_of_recruitment')
    def _current_recruitment(self):
        """
            this function is used to calculate number of employee for the recruitment
        """
        for rec in self:
            no_of_curr_rec = 0
            if rec.expected_employees and rec.state != 'done':
                employee_ids = self.env['hr.employee'].search([('date_of_join', '>=', rec.start_date), ('date_of_join', '<=', rec.end_date), ('job_id', '=', rec.job_id.id)])
                for emp in employee_ids:
                    no_of_curr_rec += 1
                rec.no_of_current_recruitment = no_of_curr_rec
                if rec.no_of_recruitment >= no_of_curr_rec:
                    rec.no_of_current_recruitment = no_of_curr_rec
                else:
                    rec.write({'expected_employees': rec.no_of_employee + rec.no_of_recruitment})
                    rec.no_of_current_recruitment = rec.expected_employees - rec.no_of_employee
                if rec.expected_employees == rec.no_of_employee:
                    rec.write({'state': 'done'})
            elif rec.state == 'done':
                rec.no_of_current_recruitment = 0
                rec.expected_employees = rec.no_of_employee
            if rec.no_of_current_recruitment < 0:
                rec.no_of_current_recruitment = 0

    # Fields HR Job Requisition
    name = fields.Char('Name', required=True, help="Name of Requisition")
    job_id = fields.Many2one('hr.job', string='Job', required=True, help="Job for which requisition required")
    expected_employees = fields.Integer(string='Total Forecasted Employees', compute='_no_of_employee', store=True)
    no_of_employee = fields.Integer(related='job_id.no_of_employee', string="Current Number of Employees", store=True)
    department_id = fields.Many2one('hr.department', string='Department', required=False, help="Department for which requisition required")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    description = fields.Text('Job Description')
    employee_ids = fields.One2many('hr.employee', 'job_id', string='Employees', groups='base.group_user')
    requirements = fields.Text('Requirements')
    no_of_recruitment = fields.Float(string="Expected in Recruitment")
    no_of_current_recruitment = fields.Integer(compute='_current_recruitment', string="Current month Recruitment", store=True, default=0)
    approved_by_recruiter = fields.Many2one('res.users', string='Approved by Recruiter', readonly=True, copy=False)
    approved_recruiter_date = fields.Datetime('Approved by Recruiter on', readonly=True, copy=False)
    approved_hof_date = fields.Datetime('Approved by HOF on', readonly=True, copy=False)
    approved_by_hof = fields.Many2one('res.users', string='Approved by HOF', readonly=True, copy=False)
    approved_hop_date = fields.Datetime('Approved by HOP on', readonly=True, copy=False)
    approved_by_hop = fields.Many2one('res.users', string='Approved by HOP', readonly=True, copy=False)
    rejected_by = fields.Many2one('res.users', string='Rejected by', readonly=True, copy=False)
    rejected_date = fields.Datetime('Rejected on', readonly=True, copy=False)
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Waiting Approval'),
                              ('approved1', 'First Approved'),
                              ('approved2', 'Second Approved'),
                              ('rejected', 'Rejected'),
                              ('launch', 'Launch'),
                              ('hold', 'Hold'),
                              ('done', 'Done')], string='Status', readonly=True, default='draft')
    user_id = fields.Many2one('res.users', 'User', readonly=True)
    min_salary = fields.Integer('Minimum Salary')
    max_salary = fields.Integer('Maximum Salary')
    approx_cost = fields.Integer('Approx Cost', compute='_calculate_approx_cost')
    is_account_manager = fields.Boolean(string='Account Manager', compute='set_account_manager')
    start_date = fields.Date(string='Start Date', copy=False)
    end_date = fields.Date(string='End Date', copy=False)

    @api.constrains('start_date', 'end_date')
    def _check_date(self):
        for rec in self:
            if rec.end_date:
                if rec.end_date < rec.start_date:
                    raise ValidationError(_('Start Date must be greater then End Date.'))

    def set_account_manager(self):
        """
            Set account manager vaule based on base setup
        """
        get_param = self.env['ir.config_parameter'].sudo().get_param('base_setup.account_manager')
        self.is_account_manager = get_param

    @api.depends('min_salary', 'max_salary')
    def _calculate_approx_cost(self):
        """
            Set approx cost based on number of recruitment employee and max salary of job position
        """
        self.ensure_one()
        self.approx_cost = self.no_of_recruitment * self.max_salary

    @api.model
    def _check_end_date(self):
        """
            Check the end date of job requisition and based on that lunch and hold job requisition record
        """
        today_date = datetime.strptime(str(fields.Date.today()), DEFAULT_SERVER_DATE_FORMAT)
        job_requisition_ids = self.search([('end_date', '!=', False), ('state', '=', 'launch')])
        job_id = []
        for job in job_requisition_ids:
            job_id.append(job.job_id.id)
        job_list = sorted(set([i for i in job_id if job_id.count(i) > 1]))
        for rec in job_requisition_ids:
            end_date = datetime.strptime(str(rec.end_date), DEFAULT_SERVER_DATE_FORMAT)
            if rec.job_id.id not in job_list and end_date <= today_date:
                rec.requisition_hold()

    @api.onchange('department_id', 'job_id')
    def onchange_department_id(self):
        """
            onchange the value based on selected job, department,
            min salary, max salary
        """
        if self.department_id and self.job_id:
            self.min_salary = self.job_id.min_salary
            self.max_salary = self.job_id.max_salary

    def unlink(self):
        """
            Delete/ remove selected record
            :return: Deleted record ID
        """
        for objects in self:
            if objects.state in ['confirm', 'approved1', 'approved2', 'done', 'launch', 'hold']:
                raise UserError(_('You cannot remove the record which is in %s state!') % objects.state)
        return super(HRJobRequisition, self).unlink()

    @api.model
    def create(self, values):
        """
            Create a new record
            :param values: Current record fields data
            :return: Newly created record ID
        """
        job_id = self.search([('job_id', '=', values.get('job_id')),
                             ('department_id', '=', values.get('department_id')),
                             ('state', 'not in', ['launch', 'done', 'rejected']),
                             ('start_date', '<=', values.get('start_date')),
                             ('end_date', '>=', values.get('end_date'))
                              ])
        if job_id:
            raise UserError(_('There is already a job requisition for this job position which is not launched yet.'))

        no_of_recruitment = values.get('no_of_recruitment', False)
        if no_of_recruitment:
            job = self.env['hr.job'].browse(values.get('job_id'))
            job.write({'no_of_recruitment': no_of_recruitment})
        res = super(HRJobRequisition, self).create(values)
        hr_emp_obj = self.env['hr.employee'].search([('job_id', '=', res.job_id.id)])
        no_of_expected = len(hr_emp_obj) + int(no_of_recruitment)
        res.write({'expected_employees': no_of_expected, 'no_of_current_recruitment': no_of_recruitment or 0})
        return res

    def write(self, values):
        """
            Update an existing record.
            :param values: Current record fields data
            :return: Current update record ID
        """
        if values.get('job_id') and values.get('department_id'):
            job_id = self.search([('job_id', '=', values['job_id']),
                                  ('department_id', '=', values['department_id']),
                                  ('state', 'not in', ['launch', 'rejected']),
                                  ('start_date', '<=', values.get('start_date')),
                                  ('end_date', '>=', values.get('end_date'))
                                  ])
            if job_id:
                raise UserError(_('There is already a job requisition for this job position which is not launched yet.'))
        no_of_recruitment = values.get('no_of_recruitment')
        if no_of_recruitment and values.get('job_id'):
            job = self.env['hr.job'].browse(values.get('job_id'))
            job.write({'no_of_recruitment': no_of_recruitment})
        res = super(HRJobRequisition, self).write(values)
        if 'no_of_recruitment' in values:
            if self.state == 'draft':
                job = self.env['hr.job'].browse(self.job_id.id)
                job.write({'no_of_recruitment': no_of_recruitment})
                hr_emp_obj = self.env['hr.employee'].search([('job_id', '=', self.job_id.id)])
                no_of_rec = len(hr_emp_obj) + no_of_recruitment
                self.write({'expected_employees': no_of_rec})
        return res

    @api.onchange('department_id')
    def onchange_department(self):
        """
            This function is used to set job ID and hof ID based on Department ID
        """
        res = {'domain': {}}
        self.job_id = False
        res['domain'].update({'job_id': [('id', 'in', [])]})
        if self.department_id:
            department = self.department_id
            job_ids = self.env['hr.job'].search([('department_id', '=', department.id)])
            self.company_id = department.company_id.id
            #self.hof_id = department.manager_id.id
            self.job_id = False
            res['domain'].update({'job_id': [('id', 'in', job_ids.ids)]})
        return res

    @api.onchange('job_id')
    def onchange_job(self):
        """
            this function is used to set company ID, Department ID and Description based on job ID
        """
        self.company_id = False
        if self.job_id:
            self.job_id.no_of_hired_employee = 0
            self.job_id.no_of_recruitment = 0
            self.company_id = self.job_id.company_id.id
            self.department_id = self.job_id.department_id.id
            self.description = self.job_id.description or ''

    def requisition_confirm(self):
        """
            sent the status of generating job requisition his/her in confirm state
        """
        self.ensure_one()
        line_manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid), ('is_hod', '=', True)])
        if line_manager and line_manager[0]:
            self.write({'state': 'confirm',
                        'approved_by_recruiter': self.env.uid,
                        'approved_recruiter_date': datetime.today()})
            self.message_post(message_type="email", subtype_xmlid='mail.mt_comment', body=_('Job Requistion Confirmed.'))
        else:
            raise ValidationError(_('You have no rights to confirm this record please contact your administrator!!'))

    def requisition_first_approval(self):
        """
            sent the status of generating job requisition his/her in approved1 state
        """
        self.ensure_one()
        hod = self.env['hr.employee'].search([('user_id', '=', self.env.uid), ('is_hod', '=', True)])
        if hod and hod[0]:
            self.write({'state': 'approved1',
                        'approved_by_hof': self.env.uid,
                        'approved_hof_date': datetime.today()})
            self.message_post(message_type="email", subtype_xmlid='mail.mt_comment', body=_('Job Requistion approved.'))
        else:
            raise ValidationError(_('You have no rights to confirm this record please contact your administrator!!'))

    def requisition_second_approval(self):
        """
            sent the status of generating job requisition his/her in approved2 state
        """
        self.ensure_one()
        self.write({'state': 'approved2',
                    'approved_by_hop': self.env.uid,
                    'approved_hop_date': datetime.today()})
        self.message_post(message_type="email", subtype_xmlid='mail.mt_comment', body=_('Job Requistion approved.'))

    def requisition_rejected(self):
        """
            sent the status of generating job requisition his/her in rejected state
        """
        self.ensure_one()
        self.write({'state': 'rejected',
                    'rejected_by': self.env.uid,
                    'rejected_date': datetime.today()})
        self.message_post(message_type="email", subtype_xmlid='mail.mt_comment', body=_('Job Requistion Reject.'))

    def requisition_launch(self):
        """
            sent the status of generating job requisition his/her in approved1 launch state
        """
        self.ensure_one()
        partner_ids = []
        for record in self:
            if record.approved_by_recruiter.id and record.approved_by_hof.id and record.approved_by_hop.id:
                partner_ids.append(record.approved_by_recruiter.partner_id.id)
                partner_ids.append(record.approved_by_hof.partner_id.id)
                partner_ids.append(record.approved_by_hop.partner_id.id)
                self.message_subscribe(partner_ids=partner_ids)
        self.write({'state': 'launch'})
        self.message_post(message_type="email", subtype_xmlid='mail.mt_comment', body=_('Job Requistion Launch.'))

    def requisition_hold(self):
        """
            sent the status of generating job requisition his/her in hold state
        """
        self.ensure_one()
        self.state = 'hold'
        self.message_post(message_type="email", subtype_xmlid='mail.mt_comment', body=_('Job Requistion Hold.'))

    def requisition_done(self):
        """
            sent the status of generating job requisition his/her in done state
        """
        self.ensure_one()
        self.state = 'done'
        self.message_post(message_type="email", subtype_xmlid='mail.mt_comment', body=_('Job Requistion Done'))

    def set_to_draft(self):
        """
            sent the status of generating job requisition his/her in draft state
        """
        self.ensure_one()
        self.state = 'draft'
        self.message_post(message_type="email", subtype_xmlid='mail.mt_comment', body=_('Job Requistion Set to Draft'))
