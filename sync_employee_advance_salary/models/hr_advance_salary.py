# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
from dateutil import relativedelta


class EmployeeAdvanceSalary(models.Model):
    _name = "hr.advance.salary"
    _description = "Advance Salary Request"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'

    name = fields.Char(string='Reference', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, default=lambda self: self.env['hr.employee'].get_employee())
    job_id = fields.Many2one('hr.job', string='Job Title', related='employee_id.job_id', readonly=True)
    department_id = fields.Many2one('hr.department', string='Department', related='employee_id.department_id', readonly=True)
    request_date = fields.Datetime(string='Request Date', required=True, default=datetime.today(), readonly=True)
    request_amount = fields.Float(string='Request Amount')
    currency_id = fields.Many2one('res.currency', related='employee_id.company_id.currency_id', string='Currency', readonly=True)
    confirm_date = fields.Datetime(string='Confirmed Date', readonly=True, copy=False)
    confirm_by = fields.Many2one('res.users', string='Confirm By', readonly=True, copy=False)
    approved1_date = fields.Datetime(string='Approved Date(HR)', readonly=True, copy=False)
    approved1_by = fields.Many2one('res.users', string='Approved By(HR)', readonly=True, copy=False)
    approved2_date = fields.Datetime(string='Approved Date(Payroll)', readonly=True, copy=False)
    approved2_by = fields.Many2one('res.users', string='Approved By(Payroll)', readonly=True, copy=False)
    paid_date = fields.Datetime(string='Paid Date', readonly=True)
    paid_by = fields.Many2one('res.users', string='Paid By', readonly=True)
    company_id = fields.Many2one('res.company', related='employee_id.company_id', string='Company', readonly=True)
    # payment_id = fields.Many2one('account.payment', string='Payment', readonly=True)
    payment_entry_id = fields.Many2one('account.move', string='Payment Entry')
    paid_amount = fields.Float(string='Paid Amount', readonly=True, copy=False)
    payslip_line_ids = fields.One2many('salary.installment.line', 'advance_salary_id')
    user_id = fields.Many2one('res.users', required=True, default=lambda self: self.env.user)
    reason = fields.Text('Reason for Advance', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('approve1', 'First Approval'),
        ('approve2', 'Approved'),
        ('paid', 'Paid'),
        ('done', 'Done'),
        ('refuse', 'Refuse'),
        ], default="draft", tracking=True)
    payment = fields.Selection([('partially', 'Partially'), ('fully', 'Fully')], string='Payment based on ',
                               default='fully')
    duration_month = fields.Integer('Payment Duration(month)', copy=False)
    amount_paid = fields.Float('Amount Paid', copy=False)
    amount_to_pay = fields.Float('Amount to pay', compute='_compute_amount_to_pay', copy=False)
    deduction_amount = fields.Float('Deduction Amount', digits='Account', copy=False)
    payment_start_date = fields.Date('Payment Start Date', copy=False, tracking=True)
    payment_end_date = fields.Date('Payment End Date', copy=False)

    @api.depends('request_amount', 'payslip_line_ids', 'payslip_line_ids.amount')
    def _compute_amount_to_pay(self):
        for rec in self:
            rec.amount_to_pay = rec.request_amount - rec.amount_paid

    @api.constrains('request_date', 'payment_start_date')
    def _check_payment_start_date(self):
        if any(self.filtered(lambda l: l.payment_start_date and l.payment_start_date < l.request_date.date())):
            raise UserError(_("Payment start date must be greater or equal to request date."))

    def calculate_button_action(self):
        if self.payment == 'partially':
            if self.duration_month == 0:
                raise ValidationError(_('Please enter proper value for Payment Duration'))
            elif self.request_amount and self.duration_month and self.payment_start_date:
                self.payment_end_date = self.payment_start_date + relativedelta.relativedelta(months=self.duration_month)
                self.deduction_amount = self.request_amount / self.duration_month

    def action_confirm(self):
        if not self.request_amount:
            raise ValidationError(_("Requested amount must be greater than 0"))
        if self.request_amount:
            advance_salary_id = self.search([('employee_id', '=', self.employee_id.id),
                                             ('id', '!=', self.id),
                                             ('state', 'not in', ['done', 'refuse'])])
            if advance_salary_id:
                raise ValidationError(_('You already generate advance salary request which is in process.'))
            wage = self.env['hr.contract'].sudo().search([('employee_id', '=', self.employee_id.id),
                                                          ('state', '=', 'open')], limit=1).wage
            limit = (wage * self.sudo().job_id.advance_salary_limit) / 100
            if self.request_amount > limit:
                raise ValidationError(_("Requested amount exceed the advance salary amount limit \n"
                                        "Please contact your HR Manager."))

            self.write({'state': 'confirm',
                            'confirm_date': datetime.today(),
                            'confirm_by': self.env.uid})

    def action_approve1(self):
        self.write({'state': 'approve1',
                    'approved1_date': datetime.today(),
                    'approved1_by': self.env.uid
                    })

    def action_approve2(self):
        self.write({'state': 'approve2',
                    'approved2_date': datetime.today(),
                    'approved2_by': self.env.uid})

    def action_paid(self):
        """
            sent the status of generating request in 'paid' state
        """
        context = dict(self.env.context or {})
        context['default_advance_salary_id'] = self.id
        return {
            'name': _('Advance Salary Payment'),
            'type': 'ir.actions.act_window',
            'context': context,
            'view_mode': 'form',
            'res_model': 'advance.salary.payment',
            'view_id': self.env.ref('sync_employee_advance_salary.view_advance_salary_payment_form').id,
            'target': 'new',
        }

    def action_refuse(self):
        self.state = 'refuse'
        self.action_mail_send()

    def unlink(self):
        """
            Delete/ remove selected record
            :return: Deleted record ID
        """
        for record in self.filtered(lambda s: s.state != 'draft'):
            raise UserError(_('You cannot remove the record which is not in draft state!'))
        return super(EmployeeAdvanceSalary, self).unlink()

    @api.model_create_multi
    def create(self, vals_list):
        """
            Create a new record
            :return: Newly created record ID
        """
        for values in vals_list:
            if 'company_id' in values:
                values['name'] = self.env['ir.sequence'].with_context(force_company=values['company_id']).next_by_code(
                    'advance_salary') or _('New')
            else:
                values['name'] = self.env['ir.sequence'].next_by_code('advance_salary') or _('New')
        res = super(EmployeeAdvanceSalary, self).create(vals_list)
        return res

    def action_mail_send(self, position=None):
        """
        This function compose an email by default
        """
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        template_id = False
        try:
            if self.state == 'done':
                template_id = ir_model_data._xmlid_lookup('sync_employee_advance_salary.email_template_advance_salary_request_done')[2]
            elif self.state == 'refuse':
                template_id = ir_model_data._xmlid_lookup('sync_employee_advance_salary.email_template_advance_salary_request_refuse')[2]
        except ValueError:
            template_id = False

        if template_id:
            template = self.env['mail.template'].browse(template_id)
            template.send_mail(self.id, force_send=True, raise_exception=False, email_values=None)
        return True


class SalaryInstallmentLine(models.Model):
    _name = 'salary.installment.line'
    _description = 'Salary Installment Line'

    advance_salary_id = fields.Many2one('hr.advance.salary')
    payslip_id = fields.Many2one('hr.payslip', 'Payslip', required=True)
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    date = fields.Date('Date', required=True)
    amount = fields.Float('Deduction Amount', digits='Account', required=True)
