# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo import tools, _


class HREndServiceBenifits(models.Model):
    _name = 'hr.end.service.benefit'
    _description = 'Employee End Of Service Benefits'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    @api.constrains('total_taken_amount', 'amount')
    def _check_amounts(self):
        for record in self:
            diff = record.total_deserved_amount - record.total_taken_amount
            if diff < record.amount:
                raise ValidationError('Your have exceed the residual amount')

    @api.constrains('date')
    def unique_end_service_benefit_date_per_employee(self):
        """Constraint to prevent create 2 end service benefits at the same day for them same employee"""
        for record in self:
            if record.date:
                end_service_benefit_ids = self.env['hr.end.service.benefit'].search(
                    [('employee_id', '=', record.employee_id.id), ('date', '=', record.date),
                     ('state', 'not in', ['cancel'])])
                if len(end_service_benefit_ids) > 1:
                    raise ValidationError(_('Employee has another end service benefit that date'))

    @api.constrains('total_deserved_amount')
    def _check_total_deserved_amount(self):
        for record in self:
            if record.total_deserved_amount == 0:
                raise ValidationError(record.end_service_benefit_type_id.zero_message)

    def _default_employee(self):
        """:returns current logged in employee using configured employee"""
        return self.env.context.get('default_employee_id') or self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1)

    @api.depends('hiring_date', 'date')
    def _compute_period(self):
        for record in self:
            if record.hiring_date:
                hiring_date = record.hiring_date
                period_days = relativedelta(record.date, hiring_date)
                record.years = period_days.years
                record.months = period_days.months
                record.days = period_days.days
                period = period_days.years + (period_days.months / 12.0) + (period_days.days / 365.0)
                record.service_period = period

    @api.depends('employee_id', 'service_period', 'end_service_benefit_type_id', 'date',
                 'total_holiday_deserved_amount', 'type', 'payment_type', 'other_amount')
    def _compute_total_deserved_amount(self):
        for record in self:
            contract_id = self.env['hr.contract'].search(
                [('employee_id', '=', record.employee_id.id), ('state', '=', 'open')],
                limit=1, order='id desc')
            if contract_id:
                wage = contract_id.wage
                allowances = 0
                if record.payment_type == 'wage_allowance':
                    allowances = sum(contract_id.allowances_ids.mapped('amount'))
                total = 0.0
                service_period = record.years + (record.months / 12.0) + (record.days / 365.0)
                if record.end_service_benefit_type_id.deserved_after <= service_period:
                    residual = service_period
                    total_taken_years = 0
                    for line in record.end_service_benefit_type_id.line_ids:
                        if residual > line.deserved_for - total_taken_years:
                            total += line.deserved_months * (line.deserved_for - total_taken_years) * (
                                    wage + allowances)
                            total_taken_years = line.deserved_for
                            residual = service_period - line.deserved_for
                        else:
                            total += line.deserved_months * residual * (wage + allowances)
                            total_taken_years += residual
                            residual = 0.0
                other_amount = record.other_amount if record.type == 'ending_service' else 0
                record.total_deserved_amount = total + (record.total_holiday_deserved_amount or 0) + other_amount

    @api.depends('employee_id', 'holiday_line_ids', 'holiday_line_ids.remaining_leaves', 'type', 'payment_type')
    def _compute_total_holiday_deserved_amount(self):
        for record in self:
            total = 0.0
            if record.type == 'ending_service':
                contract_id = self.env['hr.contract'].search(
                    [('employee_id', '=', record.employee_id.id), ('state', '=', 'open')],
                    limit=1, order='id desc')
                if contract_id:
                    wage = contract_id.wage
                    allowances = 0
                    if record.payment_type == 'wage_allowance' and contract_id.allowances_ids:
                        allowances = sum(contract_id.allowances_ids.mapped('amount'))
                    total = 0.0
                    for line in record.holiday_line_ids:
                        if line.pay:
                            total += line.remaining_leaves * ((wage + allowances) / 30)
            record.total_holiday_deserved_amount = total

    @api.depends('employee_id', 'payslip_id', 'payslip_id.line_ids', 'days_number', 'type',
                 'payment_type')
    def _compute_total_payslip_deserved_amount(self):
        category_id = self.env.user.company_id.category_id
        for record in self:
            payslip_total = 0
            if record.type == 'ending_service' and category_id:
                net_lines = self.env['hr.payslip.line'].search([
                    ('slip_id', '=', record.payslip_id.id), ('category_id', '=', category_id.id)
                ])
                for line in net_lines:
                    payslip_total += line.total
            record.total_payslip_deserved_amount = payslip_total

    @api.depends('employee_id')
    def _compute_total_taken_amount(self):
        for record in self:
            benefits_ids = self.env['hr.end.service.benefit'].search([
                ('employee_id', '=', record.employee_id.id),
                ('state', 'in', ['validated', 'paid']),
            ])
            sum = 0
            for benefits_id in benefits_ids:
                sum += benefits_id.amount
            record.total_taken_amount = sum

    @api.depends('total_deserved_amount', 'total_taken_amount')
    def _compute_available_amount(self):
        for record in self:
            record.available_amount = record.total_deserved_amount - record.total_taken_amount

    @api.depends('state')
    def _compute_payment_button_invisible(self):
        for record in self:
            record.payment_button_invisible = True
            if record.state != 'validated':
                record.payment_button_invisible = False
            if record.payment_id:
                record.payment_button_invisible = False

    @api.depends('total_deserved_amount', 'total_payslip_deserved_amount')
    def _compute_total_reward(self):
        for record in self:
            record.total_reward = record.total_deserved_amount + record.total_payslip_deserved_amount

    name = fields.Char(string='Reference', copy=False, default=_('New'),
                       tracking=True)
    state = fields.Selection(string="State", tracking=True,
                             selection=[('draft', 'Draft'),
                                        ('confirmed', 'Confirmed'),
                                        ('validated', 'Validated'),
                                        ('paid', 'Paid'),
                                        ('cancel', 'Cancelled'), ],
                             default='draft', copy=False)
    employee_id = fields.Many2one('hr.employee', string='Employee', index=True,
                                  # readonly=True,
                                  # states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
                                  tracking=True)
    department_id = fields.Many2one(comodel_name="hr.department", string="Department",
                                    related='employee_id.department_id', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    date = fields.Date(string="Date", default=datetime.now().strftime('%Y-%m-%d'), tracking=True,
                       copy=False)
    type = fields.Selection(string="Reward Type",
                            selection=[('replacement', 'Replacement'), ('ending_service', 'Ending Service'), ],
                            default='replacement', )
    payment_type = fields.Selection(string="Payment Type",
                                    selection=[('wage', 'Wage'), ('wage_allowance', 'Wage + Allowances'), ],
                                    default='wage_allowance', required=True)
    end_service_benefit_type_id = fields.Many2one(comodel_name="hr.end.service.benefit.type", string="ES Reason", )
    hiring_date = fields.Date(string="Hiring Date", related='employee_id.hiring_date', store=True)
    years = fields.Integer(string="Years", compute=_compute_period, store=True)
    months = fields.Integer(string="Months", compute=_compute_period, store=True)
    days = fields.Integer(string="Days", compute=_compute_period, store=True)
    service_period = fields.Float(string="Service Period In Years", compute=_compute_period, store=True)
    notes = fields.Text(string="Notes", tracking=True)
    company_id = fields.Many2one('res.company', string='Company', related='employee_id.company_id', store=True)
    total_holiday_deserved_amount = fields.Float(string="Total Time Off Deserved Amount",
                                                 compute=_compute_total_holiday_deserved_amount, store=True)
    total_payslip_deserved_amount = fields.Float(string="Total Payslip Deserved Amount",
                                                 compute=_compute_total_payslip_deserved_amount, store=True)
    other_amount = fields.Float(string="Other Amount")
    total_deserved_amount = fields.Float(string="ESR Deserved Amount", compute=_compute_total_deserved_amount,
                                         store=True)
    total_taken_amount = fields.Float(string="Previously ESR Disbursed Amount", compute=_compute_total_taken_amount,
                                      store=True)
    available_amount = fields.Float(string="Available to Disbursed", compute=_compute_available_amount, store=True)
    amount = fields.Float(string="Reward Requested Amount", required=False, )
    payment_id = fields.Many2one(comodel_name="account.payment", string="Reward Payment", copy=False, )
    payslip_payment_id = fields.Many2one(comodel_name="account.payment", string="Payslip Payment", copy=False, )
    account_move_id = fields.Many2one(comodel_name="account.move", string="Expense entry", copy=False, )
    payment_button_invisible = fields.Boolean(compute=_compute_payment_button_invisible)
    holiday_line_ids = fields.One2many(comodel_name="hr.end.benefit.holiday.line", inverse_name="reward_id")
    payslip_id = fields.Many2one(comodel_name="hr.payslip", string="Payslip")
    days_number = fields.Float(string="Last Month Worked Days Number", default=30)
    total_reward = fields.Float(string="Total ESR, Payslip, and Time Off", compute=_compute_total_reward, store=True)

    @api.onchange('employee_id', 'type')
    def _onchange_employee_id(self):
        if self.type == 'ending_service':
            allocation_ids = self.env['hr.leave.allocation'].search(
                [('employee_id', '=', self.employee_id.id),
                 ('state', 'not in', ['draft', 'cancel', 'refuse'])])
            holiday_status_ids = allocation_ids and allocation_ids.mapped('holiday_status_id')
            for line in self.holiday_line_ids:
                line.unlink()
            lines_ids = []
            for holiday_status_id in holiday_status_ids:
                data_days = {}
                remaining_leaves = 0
                employee_id = self.employee_id and self.employee_id or False
                if employee_id:
                    # data_days = holiday_status_id.get_days(employee_id.id)
                    data_days = holiday_status_id.get_employees_days([employee_id.id])[employee_id.id]
                for holiday_status in holiday_status_id:
                    result = data_days.get(holiday_status.id, {})
                    remaining_leaves = result.get('remaining_leaves', 0)
                    if holiday_status_id.request_unit == 'hour':
                        remaining_leaves = remaining_leaves / (
                                employee_id.company_id.number_of_hours_per_day and employee_id.company_id.number_of_hours_per_day or 8)
                    elif holiday_status_id.request_unit == 'half_day':
                        remaining_leaves = remaining_leaves / 2
                lines_ids.append((0, 0, {'holiday_id': holiday_status_id.id,
                                         'remaining_leaves': remaining_leaves}))
            self.holiday_line_ids = lines_ids

    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise ValidationError(_('You can only delete draft end service benefits'))
        res = super(HREndServiceBenifits, self).unlink()
        return res

    def action_submit(self):
        for record in self:
            group_manager = self.env.ref('hr.group_hr_manager')
            recipient_partners = []
            mail_server = self.env['ir.mail_server'].sudo().search([], order="sequence asc", limit=1)
            for recipient in group_manager[0].users:
                recipient_partners.append(
                    (4, recipient.partner_id.id)
                )
            template = False
            if recipient_partners and mail_server:
                template = self.env['ir.model.data'].get_object('hr_end_service_benefits',
                                                                'email_es_request_submission')

            if template:
                mail_template = self.env['mail.template'].browse(template.id)
                mail_id = mail_template.send_mail(record.id)
                mail = self.env['mail.mail'].browse([mail_id])
                mail.recipient_ids = recipient_partners
            if record.amount <= 0:
                raise ValidationError(_('You can not confirm rewards with amount of zero'))
            SequenceObj = self.env['ir.sequence']
            number = SequenceObj.next_by_code('hr.end.service.benefit')
            record.name = number
        record.write({'state': 'confirmed', 'name': number})

    def action_validate(self):
        for record in self:
            group_manager = self.env.ref('account.group_account_manager')
            recipient_partners = []
            mail_server = self.env['ir.mail_server'].sudo().search([], order="sequence asc", limit=1)
            for recipient in group_manager[0].users:
                recipient_partners.append(
                    (4, recipient.partner_id.id)
                )
            template = False
            if recipient_partners and mail_server:
                template = self.env['ir.model.data'].get_object('hr_end_service_benefits',
                                                                'email_es_request_payment_request')
            if template:
                mail_template = self.env['mail.template'].browse(template.id)
                mail_id = mail_template.send_mail(record.id)
                mail = self.env['mail.mail'].browse([mail_id])
                mail.recipient_ids = recipient_partners

            record.write({'state': 'validated'})
            if record.type == 'ending_service':
                record.employee_id.toggle_active()
                contract_ids = self.env['hr.contract'].search(
                    [('employee_id', '=', record.employee_id.id), ('state', '=', 'open')],
                    order='id desc')
                for contract_id in contract_ids:
                    contract_id.state = 'cancel'

    def action_draft(self):
        for record in self:
            record.write({'state': 'draft'})
            if record.payment_id:
                record.payment_id.action_draft()

    def action_cancel(self):
        for record in self:
            record.write({'state': 'cancel'})
            if record.payment_id:
                record.payment_id.cancel()
            if record.account_move_id:
                record.account_move_id.reverse_moves(record.account_move_id.date,
                                                     record.account_move_id.journal_id or False)


class HolidaysReward(models.Model):
    _name = 'hr.end.benefit.holiday.line'
    _description = 'Holiday Reward'

    def _compute_leaves(self):
        for record in self:
            if record.reward_id and record.reward_id.type == 'ending_service':
                data_days = {}
                employee_id = record.reward_id and record.reward_id.employee_id or False
                if employee_id:
                    # data_days = record.holiday_id.get_days(employee_id.id)
                    data_days = record.holiday_id.get_employees_days([employee_id.id])[employee_id.id]

                for holiday_status in record.holiday_id:
                    if data_days:
                        result = data_days.get(holiday_status.id, {})
                        record.remaining_leaves = result.get('remaining_leaves', 0)
                        if holiday_status.request_unit == 'hour':
                            record.remaining_leaves = record.remaining_leaves / (
                                    employee_id.company_id.number_of_hours_per_day and employee_id.company_id.number_of_hours_per_day or 8)
                        elif holiday_status.request_unit == 'half_day':
                            record.remaining_leaves = record.remaining_leaves / 2
            else:
                record.remaining_leaves = 0

    holiday_id = fields.Many2one(comodel_name="hr.leave.type", string="Holiday", required=False, )
    reward_id = fields.Many2one(comodel_name="hr.end.service.benefit", )
    employee_id = fields.Many2one(comodel_name="hr.employee", related='reward_id.employee_id')
    remaining_leaves = fields.Float(string="Remaining Leaves", compute=_compute_leaves, )
    pay = fields.Boolean(string="Pay As Reward")
