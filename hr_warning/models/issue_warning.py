# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import timedelta
from odoo.exceptions import UserError


class IssueWarning(models.Model):
    _name = "issue.warning"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Issue Warning'

    name = fields.Char(string='Name', default='New')
    warning_date = fields.Date(string='Warning Date', default=fields.Date.today())
    warning_types = fields.Many2many('warning.type', string='Warning Types', required=True)
    warning_action = fields.Selection([('expiry', 'Expiry Period'), ('deduct', 'Deduct from Salary or not'), ('prohibit', 'Prohibit Benefit Upgrades')], string="Warning Action", required=True)
    user_id = fields.Many2one('res.users', string='Confirmed By', required=True, default=lambda self: self.env.user)
    start_date = fields.Date(string='Start Date', default=fields.Date.today())
    end_date = fields.Date(string='End Date')
    is_deduction_from_salary = fields.Boolean(string='Is Deduct from Salary')
    deduct_type = fields.Selection([('amount', 'By Amount'), ('days', 'By Days'), ('hours', 'By Hours'), ('percentage', 'By Percentage')], string='Deduct type')
    description = fields.Text(string='Description', required=True)
    target_group = fields.Selection([('employee', 'One Employee'), ('department', 'Department Wise'), ('job', 'Job Profile'), ('all_employee', 'All Employees')], string='Target Group', default='employee')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    department_ids = fields.Many2many('hr.department', string='Department')
    job_ids = fields.Many2many('hr.job', string='Job Profile')
    employee_ids = fields.Many2many('hr.employee', string='Employees')
    color = fields.Integer(string='Color')
    group_mail = fields.Boolean(string='Group Mail')
    no_of_days = fields.Float(string='No of Days')
    no_of_hours = fields.Float(string='No of Hours')
    percentage = fields.Float(string='Percentage')
    ded_amt = fields.Float(string='Amount')
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirmed'),
                              ('done', 'Done'),
                              ('cancel', 'Cancelled')], string="Status", default='draft', copy=False, tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            values['name'] = self.env['ir.sequence'].next_by_code('warning')
        return super(IssueWarning, self).create(vals_list)

    @api.onchange('warning_action')
    def onchange_warning_action(self):
        """
            onchange the value based on selected warning_action
        """
        self.is_deduction_from_salary = False
        self.warning_types = False
        self.deduct_type = False
        self.no_of_days = False
        self.no_of_hours = False
        self.ded_amt = False
        self.percentage = False
        res = {}
        if self.warning_action:
            warning_types = self.env['warning.type'].search([('warning_action', '=', self.warning_action)])
            self.warning_types = [(6, 0, warning_types.ids)]
            res['domain'] = {'warning_types': [('warning_action', '=', self.warning_action)]}
        return res

    @api.onchange('department_ids')
    def onchange_department_ids(self):
        """
            set the value of employee_ids based on selected department_ids
        """
        employees = self.env['hr.employee'].search([('department_id', 'in', self.department_ids.ids)])
        self.employee_ids = [(6, 0, employees.ids)]

    @api.onchange('job_ids')
    def onchange_job_ids(self):
        """
            set the value of employee_ids based on selected job_ids
        """
        employees = self.env['hr.employee'].search([('job_id', 'in', self.job_ids.ids)])
        self.employee_ids = [(6, 0, employees.ids)]

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        """
            set the value of employee_ids based on selected employee_id
        """
        if self.employee_id:
            self.employee_ids = [(6, 0, self.employee_id.ids)]

    @api.onchange('target_group')
    def onchange_target_group(self):
        """
            Onchange the value based on selected target_group
        """
        context = dict(self.env.context) or {}
        if not context.get('default_employee_id'):
            self.employee_id = False
        self.employee_ids = False
        self.department_ids = False
        self.job_ids = False
        self.group_mail = False
        if self.target_group == 'all_employee':
            employees = self.env['hr.employee'].search([])
            self.employee_ids = [(6, 0, employees.ids)]

    @api.onchange('deduct_type')
    def onchange_deduct_type(self):
        """
            Onchange the value based on selected deduct type
        """
        self.ded_amt = False
        self.no_of_days = False
        self.no_of_hours = False
        self.percentage = False

    def mail_to(self):
        """
            return partner_ids
        """
        rec = []
        if self.employee_ids:
            for employee in self.employee_ids:
                if employee and employee.user_id:
                    rec.append(str(employee.user_id.partner_id.id))
        record = ', '.join(rec)
        return record

    def action_mail_send(self):
        """
            This function send an email by default
        """
        try:
            template_id = self.env.ref('hr_warning.email_template_warning_confirm_partner')
        except ValueError:
            template_id = False
        warning = []
        for warning_type in self.warning_types:
            warning.append(warning_type.name)
        if template_id and self.group_mail:
            template_id.with_context({'warning': ', '.join(warning)}).send_mail(self.id, force_send=True, raise_exception=False, email_values=None)
        elif template_id and not self.group_mail:
            if self.employee_ids:
                for employee in self.employee_ids:
                    if employee.user_id:
                        partner_id = employee.user_id.partner_id.id
                        template_id.with_context({'email_to': partner_id,
                                               'warning': ', '.join(warning)}).send_mail(self.id, force_send=True, raise_exception=False, email_values=None)
        return True

    def _add_followers(self, partner_ids=[]):
        """
            employee and manager add in followers
        """
        partner_ids.append(self.env.user.partner_id.id)
        for emp in self.employee_ids:
            if emp.user_id:
                partner_ids.append(emp.user_id.partner_id.id)
        self.message_subscribe(partner_ids=partner_ids)

    def action_hop_send_mail(self):
        """
            send mail to employee's branch HOP
        """
        warning_expiry_date = self.warning_date - timedelta(days=180)
        warning_ids = self.search([('state', '=', 'done'), ('employee_ids', 'in', self.employee_ids.ids), ('warning_date', '>=', warning_expiry_date), ('warning_date', '<=', self.warning_date)])
        emp_branch_dict = {}
        if warning_ids:
            group_ids = self.env['hr.groups.configuration'].search([])
            hop_dict = {}
            for group in group_ids:
                employee_ids = self.env['hr.employee'].search([('id', 'in', self.employee_ids.ids), ('branch_id', '=', group.branch_id.id), ('issue_warning_ids', 'in', warning_ids.ids)])
                emp_list = []
                for rec in employee_ids:
                    emp_list.append(rec.name)
                    hop_list = []
                    for hop in group.hop_ids:
                        hop_list.append(hop.user_id.partner_id.id)
                    hop_dict.update({group.branch_id.id: hop_list})
                emp_branch_dict.update({group.branch_id.id: emp_list})
            for key, value in hop_dict.items():
                val = emp_branch_dict.get(key)
                try:
                    template_id = self.env.ref('hr_warning.email_template_warning_alert')
                except ValueError:
                    template_id = False
                warning = []
                for warning_type in self.warning_types:
                    warning.append(warning_type.name)
                if template_id and warning and value and val:
                    hop_ids = str([value]).replace('[', '').replace(']', '')
                    template_id.with_context({'warning': ', '.join(warning),
                                              'hop_id': hop_ids,
                                              'employee_ids': ', '.join(val)}).send_mail(self.id, force_send=True, raise_exception=False, email_values=None)
                self._add_followers(value)

    def action_confirm(self):
        """
            sent the status of generating warning in confirm state
        """
        self.action_mail_send()
        self._add_followers()
        self.action_hop_send_mail()
        self.state = 'confirm'

    def action_done(self):
        """
            sent the status of generating warning in done state
        """
        # action_done not work (payroll)module flow remaing in odoo-13
        self.action_mail_send()
        for rec in self:
            if rec.warning_action == 'deduct':
                if not rec.is_deduction_from_salary:
                    raise UserError(_('You need to select Is Deduct from Salary option.'))
                other_payslip_obj = self.env['other.hr.payslip']
                # create other allowance
                payslip_data = {'employee_id': rec.employee_id.id,
                                'description': rec.description,
                                'calc_type': rec.deduct_type,
                                'amount': rec.ded_amt or 0,
                                'percentage': rec.percentage or 0,
                                'no_of_days': rec.no_of_days or 0,
                                'no_of_hours': rec.no_of_hours or 0,
                                'state': 'done',
                                'operation_type': 'deduction',
                                }
                if rec.target_group == 'employee' and rec.warning_action == 'deduct':
                    payslip_id = other_payslip_obj.create(payslip_data)
                elif rec.target_group != 'employee' and rec.warning_action == 'deduct':
                    for line in rec.employee_ids:
                        payslip_data = {'employee_id': line.id,
                                        'description': rec.description,
                                        'calc_type': rec.deduct_type,
                                        'amount': rec.ded_amt or 0,
                                        'percentage': rec.percentage or 0,
                                        'no_of_days': rec.no_of_days or 0,
                                        'no_of_hours': rec.no_of_hours or 0,
                                        'state': 'done',
                                        'operation_type': 'deduction',
                                        }
                        payslip_id = other_payslip_obj.create(payslip_data)
        self.state = 'done'

    def action_cancel(self):
        """
            sent the status of generating warning in cancel state
        """
        self.state = 'cancel'

    def unlink(self):
        for rec in self:
            if rec.state not in ['draft', 'cancel']:
                raise UserError(_('You cannot remove the record which is in %s state!') % rec.state)


class HRJOb(models.Model):
    _inherit = "hr.job"

    color = fields.Integer(string='Color')
