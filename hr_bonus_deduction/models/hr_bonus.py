# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrBonusTag(models.Model):
    _name = 'hr.bonus.tag'
    _description = 'Bonus Tags'

    name = fields.Char(string='Name', index=True, required=True)


class HrBonus(models.Model):
    _name = 'hr.bonus'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hr Bonus'

    name = fields.Char(string='Name', readonly=True, copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('approved', 'Approved'),
        ('cancel', 'Cancel'),
    ], string='State', index=True, readonly=True, default='draft', copy=False, track_visibility='onchange')
    employee_ids = fields.Many2many('hr.employee', string='Employees', required=True)
    target_group = fields.Selection([
        ('employee', 'By Employees'),
        ('department', 'By Department')
    ], string='Target Group', required=True, default='employee')
    department_id = fields.Many2one('hr.department', 'Department')
    tag_ids = fields.Many2many('hr.bonus.tag', string='Tags', copy=True)
    manager_id = fields.Many2one('res.users', string='Manager', required=True,
                                 domain=lambda self: [('groups_id', '=', self.env.ref('hr.group_hr_user').id)])
    is_manager = fields.Boolean('Is Manager', compute='_compute_is_manager')
    declaration_date = fields.Date('Declaration Date', default=fields.Date.today, required=True)
    applied_date = fields.Date('Applied Date', default=fields.Date.today, required=True)
    bonus_by = fields.Selection([
        ('amount', 'Amount'),
        ('percentage', 'Percentage')
    ], string='Bonus By', readonly=True, default='amount')
    amount = fields.Float('Amount', required=True)
    summary = fields.Char('Summary')
    description = fields.Text('Description')

    @api.constrains('amount')
    def _check_bonus_amount(self):
        if self.amount <= 0:
            raise ValidationError(_('Amount must be greater than zero'))

    # @api.one
    def _compute_is_manager(self):
        if self.env.user.id == self.manager_id.id:
            self.is_manager = True
        else:
            self.is_manager = False

    @api.model
    def default_get(self, default_fields):
        # get default bonus amount
        config_parameters = self.env['ir.config_parameter'].sudo()
        bonus_amount = config_parameters.get_param('bonus_amount')

        contextual_self = self.with_context(default_amount=bonus_amount)
        return super(HrBonus, contextual_self).default_get(default_fields)

    def action_confirm(self):
        name = self.env['ir.sequence'].next_by_code('hr.bonus')
        return self.write({'state': 'confirm', 'name': name})

    def action_approved(self):
        return self.write({'state': 'approved'})

    def action_cancel(self):
        return self.write({'state': 'cancel'})

    @api.onchange('department_id', 'target_group')
    def onchange_department(self):
        employees = False
        domain = []
        if self.target_group == 'department' and self.department_id:
            domain = [('department_id', '=', self.department_id.id)]
            employees = self.env['hr.employee'].search(domain)

        self.employee_ids = employees and employees.ids or False

        return {'domain': {'employee_ids': domain}}

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'confirm':
            return self.env.ref('hr_bonus_deduction.mt_hr_bonus_confirm')
        elif 'state' in init_values and self.state == 'approved':
            return self.env.ref('hr_bonus_deduction.mt_hr_bonus_approved')
        elif 'state' in init_values and self.state == 'cancel':
            return self.env.ref('hr_bonus_deduction.mt_hr_bonus_cancel')
        return super(HrBonus, self)._track_subtype(init_values)
