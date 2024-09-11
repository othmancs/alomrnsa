# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo import tools


class AnalyticOvertime(models.Model):
    _name = 'analytic.overtime'
    _order = 'id desc'
    _description = "Analytic Overtime"
    _inherit = ['mail.thread']

    name = fields.Char('Task Name', required=True, tracking=True)
    date = fields.Date('Start Date', required=True, tracking=True)
    end_date = fields.Date('End Date', required=True, tracking=True)
    duration = fields.Float('Daily Duration', digits=(2, 2), tracking=True)
    description = fields.Text('Description')
    state = fields.Selection([
        ('tentative', 'Draft'),
        ('cancelled', 'Cancelled'),
        ('confirmed', 'Confirmed'),
        ('waiting', 'Waiting Answer'),
        ('done', 'Done'),
        ], 'Status', readonly=True, default='tentative', tracking=True)
    user_id = fields.Many2one('res.users', 'Responsible', tracking=True, default=lambda self: self.env.uid, readonly=True)
    attendee_ids = fields.One2many('analytic.overtime.attendee', 'analytic_overtime_id', string='Attendees')
    target = fields.Selection([('office', 'Office Wise'), ('company', 'Company Wise'),
                               ('department', 'Department Wise'), ('job', 'Job Profile Wise')], string="Target Group")
    branch_ids = fields.Many2many('hr.branch', string='Offices')
    company_ids = fields.Many2many('res.company', 'company_analytic_overtime_rel', 'analytic_overtime_id', 'company_id', string="Companies")
    department_ids = fields.Many2many('hr.department', string="Departments")
    job_ids = fields.Many2many('hr.job', 'job_analytic_overtime_rel', 'analytic_overtime_id', 'job_id', string="JOB Profiles")

    _sql_constraints = [
        ('check_dates', 'CHECK(date <= end_date)', 'Start Date must be greater than End Date!'),
    ]

    @api.onchange('user_id', 'target', 'company_ids', 'department_ids', 'job_ids', 'branch_ids')
    def onchange_target(self):
        """
            onchange the value based on selected target, user_id, branch_ids, company_ids, department_ids, job_ids
        """
        company_obj = self.env['res.company']
        emp_obj = self.env['hr.employee']
        attendees = []

        def get_mail(employee_id):
            """
                get employee email
            """
            email = ''
            if employee_id:
                employee = emp_obj.browse(employee_id)
                email = employee.work_email or employee.user_id.email or ''
                return {'value': {'email': email}}
            return {'value': {'email': email}}

        if self.target == 'office':
            self.attendee_ids = False
            for emp_id in emp_obj.search([('branch_id', 'in', self.branch_ids.ids)]):
                res = get_mail(emp_id.id)
                attendees.append({'user_id': self.user_id.id or self.env.uid,
                                  'employee_id': emp_id.id,
                                  'email': res['value']['email'] or '',
                                  'state': 'needs-action',
                                  'analytic_overtime_id': self.id,
                                  })
            self.department_ids = False
            self.job_ids = False
            self.company_ids = False
            self.attendee_ids.create(attendees)

        elif self.target == 'company':
            self.attendee_ids = False
            for emp_id in emp_obj.search([('company_id', 'in', self.company_ids.ids)]):
                res = get_mail(emp_id.id)
                attendees.append({'user_id': self.user_id.id or self.env.uid,
                                  'employee_id': emp_id.id,
                                  'email': res['value']['email'] or '',
                                  'state': 'needs-action',
                                  'analytic_overtime_id': self.id,
                                  })
            self.department_ids = False
            self.job_ids = False
            self.branch_ids = False
            self.attendee_ids.create(attendees)

        elif self.target == 'department':
            self.attendee_ids = False
            for emp_id in emp_obj.search([('department_id', 'in', self.department_ids.ids or [])]).ids:
                res = get_mail(emp_id)
                attendees.append({'user_id': self.user_id.id or self.env.uid,
                                  'employee_id': emp_id,
                                  'email': res['value']['email'] or '',
                                  'state': 'needs-action',
                                  'analytic_overtime_id': self.id
                                  })
            self.job_ids = False
            self.company_ids = False
            self.branch_ids = False
            self.attendee_ids.create(attendees)

        elif self.target == 'job':
            self.attendee_ids = False
            for emp_id in emp_obj.search([('job_id', 'in', self.job_ids.ids or [])]).ids:
                res = get_mail(emp_id)
                attendees.append({'user_id': self.user_id.id or self.env.uid,
                                  'employee_id': emp_id,
                                  'email': res['value']['email'] or '',
                                  'state': 'needs-action',
                                  'analytic_overtime_id': self.id
                                  })
            self.department_ids = False
            self.company_ids = False
            self.branch_ids = False
            self.attendee_ids.create(attendees)
        else:
            self.department_ids = False
            self.job_ids = False
            self.company_ids = False
            self.attendee_ids = False
            # self.branch_ids = False

    def create_attendees(self):
        """
            Create an Attendees and send mail
        """
        current_user = self.env.user
        for analytic in self:
            if not analytic.attendee_ids:
                raise UserError(_('Please create some invitation details!'))
            for att in analytic.attendee_ids:
                if not att.email:
                    continue
                if not att.mail_sent:
                    mail_to = att.email
                    if mail_to and (current_user.email or analytic.user_id.email or tools.config.get('email_from', False)):
                        att._send_mail(mail_to, email_from=current_user.email or analytic.user_id.email or tools.config.get('email_from', False))
        self.state = 'waiting'

    def do_confirm(self):
        """
            sent the status of overtime request in Confirm state
        """
        self.ensure_one()
        self.state = 'confirmed'

    def do_tentative(self):
        """
            sent the status of overtime request in Tentative state
        """
        self.ensure_one()
        self.state = 'tentative'

    def do_done(self):
        """
            sent the status of overtime request in Done state
        """
        self.ensure_one()
        self.state = 'done'

    def do_cancel(self):
        """
            sent the status of overtime request in Cancel state
        """
        self.ensure_one()
        self.state = 'cancelled'

    def unlink(self):
        """
            To remove the record, which is not in 'tentative' state
        """
        for rec in self:
            if not rec.state in ['tentative']:
                raise UserError(_('In order to delete a confirmed analytic overtime request, you must set to draft it before!'))
        return super(AnalyticOvertime, self).unlink()

    def copy(self, default=None):
        """
           To copy the record
        """
        return super(AnalyticOvertime, self.with_context(from_copy=True)).copy(default)


class AnalyticOvertimeAttendee(models.Model):
    _name = "analytic.overtime.attendee"
    _order = 'id desc'
    _description = "Analytic Overtime Attendee"
    _rec_name = 'analytic_overtime_id'
    _inherit = ['mail.thread']

    analytic_overtime_id = fields.Many2one('analytic.overtime', 'Analytic Overtime Request', ondelete='cascade', domain=[('state', 'not in', ['cancelled', 'done'])], tracking=True)
    state = fields.Selection([('needs-action', 'Waiting Answer'),
                              ('declined', 'Declined'),
                              ('accepted', 'Accepted')], 'Status', readonly=True, help="Status of the attendee's participation", default='needs-action', tracking=True)
    user_id = fields.Many2one('res.users', string='User', tracking=True, default=lambda self: self.env.user)
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, tracking=True)
    mail_sent = fields.Boolean('Mail Sent', default=False)
    email = fields.Char('Email', size=124, help="Email of Invited Person")

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        """
            This function is used set value of email
        """
        self.email = self.employee_id.work_email or self.employee_id.user_id.email or ''

    def _send_mail(self, mail_to, email_from=tools.config.get('email_from', False)):
        """
            Send mail for overtime to overtime attendees.
            @param email_from: email address for user sending the mail
            @return: True
            """
        try:
            template_id = self.env.ref('saudi_hr_overtime_request.email_template_create_attendee')
        except ValueError:
            template_id = False
        for att in self:
            if not att.employee_id.user_id:
                raise UserError(_("Please assign user to %s.") % att.employee_id.name)
            if att.employee_id and template_id:
                rec = template_id.with_context({'mail_to': mail_to, 'email_from': email_from}).send_mail(att.id, force_send=True, raise_exception=False)
                if rec:
                    self.mail_sent = True

    # @api.multi
    # def do_tentative(self):
    #     """
    #         update the status to tentative
    #     """
    #     self.ensure_one()
    #     self.state = 'tentative'

    def do_accept(self):
        """
            update the status to accepted
        """
        self.ensure_one()
        self.state = 'accepted'

    def do_decline(self):
        """
            update the status to declined
        """
        self.ensure_one()
        self.state = 'declined'

    @api.model
    def create(self, values):
        """
            Create a new record
            return: Newly created record ID
        """
        if self._context.get('from_copy', False):
            values.update(mail_sent=False)
        return super(AnalyticOvertimeAttendee, self).create(values)
