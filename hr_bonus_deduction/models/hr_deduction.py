# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrDeductionTag(models.Model):
    _name = 'hr.deduction.tag'
    _description = 'Deduction Tags'

    name = fields.Char(string='Name', index=True, required=True)


class HrDeduction(models.Model):
    _name = 'hr.deduction'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hr Deduction'

    name = fields.Char(string='Name', readonly=True, copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('approved', 'Approved'),
        ('cancel', 'Cancel'),
    ], string='State', index=True, readonly=True, default='draft', copy=False, track_visibility='onchange')
    employee_id = fields.Many2one('hr.employee', ondelete='cascade', string='Employee', required=True)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Department',
                                    store=True, readonly=True)
    job_id = fields.Many2one('hr.job', related='employee_id.job_id', string='Job Title', store=True, readonly=True)
    company_id = fields.Many2one('res.company', related='employee_id.company_id', string='Company', store=True,
                                 readonly=True)
    tag_ids = fields.Many2many('hr.deduction.tag', string='Tags', copy=True)
    manager_id = fields.Many2one('res.users', string='Manager', required=True,
                                 domain=lambda self: [('groups_id', '=', self.env.ref('hr.group_hr_user').id)])
    is_manager = fields.Boolean('Is Manager', compute='_compute_is_manager')
    declaration_date = fields.Date('Declaration Date', default=fields.Date.today, required=True)
    applied_date = fields.Date('Applied Date', default=fields.Date.today, required=True)
    deduction_by = fields.Selection([
        ('amount', 'Amount'),
        ('percentage', 'Percentage')
    ], string='Deduction By', readonly=True, default='amount')
    amount = fields.Float('Amount', required=True)
    summary = fields.Char(string='Summary')
    description = fields.Text('Description')

    @api.constrains('amount')
    def _check_deduction_amount(self):
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
        # get default deduction amount
        config_parameters = self.env['ir.config_parameter'].sudo()
        deduction_amount = config_parameters.get_param('deduction_amount')

        contextual_self = self.with_context(default_amount=deduction_amount)
        return super(HrDeduction, contextual_self).default_get(default_fields)

    def action_confirm(self):
        name = self.env['ir.sequence'].next_by_code('hr.deduction')
        return self.write({'state': 'confirm', 'name': name})

    def action_approved(self):
        return self.write({'state': 'approved'})

    def action_cancel(self):
        return self.write({'state': 'cancel'})

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'confirm':
            return self.env.ref('hr_bonus_deduction.mt_hr_deduction_confirm')
        elif 'state' in init_values and self.state == 'approved':
            return self.env.ref('hr_bonus_deduction.mt_hr_deduction_approved')
        elif 'state' in init_values and self.state == 'cancel':
            return self.env.ref('hr_bonus_deduction.mt_hr_deduction_cancel')
        return super(HrDeduction, self)._track_subtype(init_values)
