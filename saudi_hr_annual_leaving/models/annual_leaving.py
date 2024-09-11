# -*- coding: utf-8 -*-
# Part of odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AnnualLeaving(models.Model):
    _name = 'annual.leaving'
    _rec_name = 'year_id'
    _description = 'Annual Leaving'

    year_id = fields.Many2one('year.year', string='Year', required=True)
    leaves_details_ids = fields.One2many('leaves.details', 'annual_leaving_id', string='Leaves Details')
    is_maximum_leave_carry_forward = fields.Boolean('Maximum Leave Carry Forward')
    maximum_leave_carry_forward = fields.Float(string='No. of Maximum Leave Carry Forward')
    allocation_leave_type_id = fields.Many2one('hr.leave.type', string='Next Year Allocation Leave Type', required=False)
    applied_date = fields.Date(string='Report Date', copy=False)

    @api.constrains('leaves_details_ids')
    def check_duplicate_record(self):
        """
            Constraints for the record is overlaps for same employee or not.
        """
        for rec in self:
            emp_list = []
            for line in rec.leaves_details_ids:
                if line.employee_id.id not in emp_list:
                    emp_list.append(line.employee_id.id)
                else:
                    raise ValidationError(_('You already done %s leaves details') % line.employee_id.name)

    def unlink(self):
        if len(self.leaves_details_ids.ids) > 0:
            raise UserError(_('You cannot delete annual leave record which leave details lines are created.'))
        return super().unlink()

    def action_annual_leaving_by_employees(self):
         self.ensure_one()
         form_view = self.env.ref('saudi_hr_annual_leaving.view_annual_leaving_by_employees', False)
         return {
            'name': _('Generate Annual Leaving'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'res_model': 'annual.leaving.employees',
            'views': [(form_view.id, 'form')],
            'view_id': form_view.id,
            'target': 'new',
            'context': self.env.context,
        }

    def action_annual_leaving_carry_forward(self):
        self.ensure_one()
        if not self.allocation_leave_type_id:
            raise UserError(_('You need to select Allocation leave type for carry forward!!'))
        if not self.applied_date:
            raise UserError(_('You need to configure Applied Date!!'))

        for leave_detail in self.leaves_details_ids.filtered(lambda leave: leave.remaining_leaves > 0.0):

            carry_days = 0
            leave_encashment_details_ids = []
            leave_allocation_obj = self.env['hr.leave.allocation']
            leave_allocations = leave_allocation_obj.search([('employee_id', '=', leave_detail.employee_id.id),
                                                             ('state', '=', 'validate'),
                                                             ('holiday_status_id.is_annual_leave', '=', True),
                                                             ('date_from', '>=', self.year_id.date_start),
                                                             ('date_to', '<=', self.year_id.date_stop)])
            if self.is_maximum_leave_carry_forward:
                carry_days = self.maximum_leave_carry_forward

            for allocation in leave_allocations:
                days = 0
                remain_days = allocation.number_of_days - allocation.leaves_taken

                if self.is_maximum_leave_carry_forward:
                    days = carry_days if carry_days <= remain_days else remain_days
                else:
                    days = remain_days

                if days > 0.0:
                    leave_encashment_details_ids.append((0, 0, {'leave_allocation_id': allocation.id,
                                                            'encashment_days': days,}))
                    if self.is_maximum_leave_carry_forward:
                        carry_days -= days
                        if carry_days <= 0.0:
                            continue

            if leave_encashment_details_ids:
                encashment_vals = {'employee_id': leave_detail.employee_id.id,
                                    'encashment_type': 'carry_forward',
                                    'allocated_leaves': leave_detail.allocated_leaves,
                                    'used_leaves': leave_detail.used_leaves,
                                    'remaining_leaves': leave_detail.remaining_leaves,
                                    'updated_leaves': leave_detail.updated_leaves,
                                    'leave_details_id': leave_detail.id,
                                    'applied_date': self.applied_date,
                                    'leave_encashment_details_ids': leave_encashment_details_ids}
                encashment_id = self.env['leave.encashment'].create(encashment_vals)
                encashment_id.generate_leave_allowance()


class LeavesDetails(models.Model):
    _name = 'leaves.details'
    _description = 'Leaves Details'
    _rec_name = 'employee_id'

    @api.depends('updated_leaves', 'used_leaves')
    def compute_remaining_leaves(self):
        for rec in self:
            rec.remaining_leaves = 0.0
            if rec.updated_leaves:
                rec.remaining_leaves = rec.updated_leaves - rec.used_leaves

    def compute_leaves(self):
        leave_allocation_obj = self.env['hr.leave.allocation']
        hr_leave_obj = self.env['hr.leave']
        for rec in self:
            allocated_leaves = used_leaves = updated_leaves = 0
            allocation_ids = leave_allocation_obj.search(
                [('employee_id', '=', rec.employee_id.id), ('state', '=', 'validate'),
                 ('holiday_status_id.is_annual_leave', '=', True),
                 ('date_from', '>=', rec.year_id.date_start),
                 ('date_to', '<=', rec.year_id.date_stop),
                 ])
            if allocation_ids:
                allocated_leaves = sum(allocation.number_of_days for allocation in allocation_ids)#.mapped('number_of_days')
                used_leaves_ids = hr_leave_obj.search([('employee_id', '=', rec.employee_id.id),
                                                       ('holiday_status_id.is_annual_leave', '=', True),
                                                       ('date_from', '>=', rec.year_id.date_start),
                                                       ('date_to', '<=', rec.year_id.date_stop),
                                                       ('state', '=', 'validate'),
                                                       ])
                if used_leaves_ids:
                    used_leaves = sum(leaves.number_of_days for leaves in used_leaves_ids)
                updated_leaves = allocated_leaves
            #rec.allocated_leaves = allocated_leaves
            rec.used_leaves = used_leaves
            rec.updated_leaves = updated_leaves

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, domain=lambda self: self._get_employee_domain())
    department_id = fields.Many2one('hr.department', 'Department', related="employee_id.department_id", store=True)
    branch_id = fields.Many2one('hr.branch', 'Office', related="employee_id.branch_id", store=True)
    annual_leaving_id = fields.Many2one('annual.leaving', 'Annual Leaving')
    year_id = fields.Many2one('year.year', related='annual_leaving_id.year_id', readonly=True, store=True)

    allocated_leaves = fields.Float('Allocated Leaves', readonly=False)
    used_leaves = fields.Float('Used Leaves', readonly=True, compute='compute_leaves', store=True, compute_sudo=True)
    remaining_leaves = fields.Float(string='Remaining Leaves', compute='compute_remaining_leaves')
    updated_leaves = fields.Float('Updated Allocated leaves', compute='compute_leaves', compute_sudo=True)
    encashment_leaves = fields.Float('Encashment Leaves', readonly=True)

    cutdown_leaves_history_ids = fields.One2many('cutdown.leaves.history', 'leaves_details_id','Cutdown Leave History')
    payment_ids = fields.Many2many('account.payment', string='Payments')

    def _get_employee_domain(self):
        domain = []
        leave_allocation_obj = self.env['hr.leave.allocation']
        employees = leave_allocation_obj.search([('state', '=', 'validate'), ('holiday_status_id.is_annual_leave', '=', True)]).mapped('employee_id')
        domain.append(('id', 'in', employees.ids))
        return domain

    @api.onchange('employee_id')
    def onchange_employee(self):
        leave_allocation_obj = self.env['hr.leave.allocation']
        hr_leave_obj = self.env['hr.leave']

        for rec in self:
            if rec.employee_id:
                allocated_leaves = used_leaves = updated_leaves = 0
                allocation_ids = leave_allocation_obj.search(
                    [('employee_id', '=', rec.employee_id.id), ('state', '=', 'validate'),
                     ('holiday_status_id.is_annual_leave', '=', True),
                     ('date_from', '>=', rec.year_id.date_start),
                     ('date_to', '<=', rec.year_id.date_stop),
                     ])
                if allocation_ids:
                    allocated_leaves = sum(allocation.number_of_days for allocation in allocation_ids)
                    used_leaves_ids = hr_leave_obj.search([('employee_id', '=', rec.employee_id.id),
                                                           ('holiday_status_id.is_annual_leave', '=', True),
                                                           ('date_from', '>=', rec.year_id.date_start),
                                                           ('date_to', '<=', rec.year_id.date_stop),
                                                           ('state', '=', 'validate')
                                                           ])
                    if used_leaves_ids:
                        used_leaves = sum(leaves.number_of_days for leaves in used_leaves_ids)
                    updated_leaves = allocated_leaves
                rec.allocated_leaves = allocated_leaves
                rec.used_leaves = used_leaves
                rec.remaining_leaves = updated_leaves - used_leaves
                rec.updated_leaves = allocated_leaves

    # def write(self, values):
    #     for rec in self:
    #         if values.get('employee_id'):
    #             leave_allocation_obj = self.env['hr.leave.allocation']
    #             rec.allocated_leaves = sum(leave_allocation_obj.search([('employee_id', '=', rec.employee_id.id), ('state', '=', 'validate')]).mapped(
    #                 'number_of_days'))
    #             rec.updated_leaves = rec.allocated_leaves
    #             hr_leave_obj = self.env['hr.leave']
    #             rec.used_leaves = sum(hr_leave_obj.search([('employee_id', '=', rec.employee_id.id),
    #                                                        ('holiday_status_id.is_annual_leave', '=', True)]).mapped('number_of_days'))
    #             rec.remaining_leaves = rec.updated_leaves - rec.used_leaves
    #     return super(LeavesDetails, self).write(values)

    # @api.model
    # def create(self, values):
    #     if values.get('employee_id'):
    #         leave_allocation_obj = self.env['hr.leave.allocation']
    #         values['allocated_leaves'] = sum(leave_allocation_obj.search([('employee_id', '=', values['employee_id']), ('state', '=', 'validate')]).mapped('number_of_days'))
    #         values['updated_leaves'] = values['allocated_leaves']
    #         hr_leave_obj = self.env['hr.leave']
    #         values['used_leaves'] = sum(hr_leave_obj.search([('employee_id', '=', values['employee_id']), ('holiday_status_id.is_annual_leave', '=', True)]).mapped(
    #             'number_of_days'))
    #         values['remaining_leaves'] = values['updated_leaves'] - values['used_leaves']
    #     return super(LeavesDetails, self).create(values)

    def leave_encashment(self):
        context = dict(self._context)
        context.update({'default_leave_details_id': self.id})
        return {
            'name': 'Leave Encashment',
            'res_model': 'leave.encashment',
            'view_mode': 'form',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new',
        }

    def unlink(self):
        for rec in self:
            if rec.encashment_leaves > 0:
                raise UserError(_('You cannot delete leaves details line which encashment process already done.'))
        return super().unlink()


class CutdownLeavesHistory(models.Model):
    _name = 'cutdown.leaves.history'
    _description = 'Employees leaves history which cutdown or encashment from leaves allocation'

    leaves_details_id = fields.Many2one('leaves.details')
    holiday_status_id = fields.Many2one('hr.leave.type', required=True)
    applied_date = fields.Date(string='Applied Date', required=True)
    name = fields.Char('Name', required=True)
    other_hr_payslip_id = fields.Many2one('other.hr.payslip', 'Reference', readonly=True)
    number_of_days = fields.Float('Number of days')
    date = fields.Datetime('Date', required=True)
