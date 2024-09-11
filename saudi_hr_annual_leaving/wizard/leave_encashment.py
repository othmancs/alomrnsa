# -*- coding: utf-8 -*-
# Part of odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime


class LeaveEncashment(models.TransientModel):
    _name = 'leave.encashment'
    _description = 'Leave Encashment'

    leave_details_id = fields.Many2one('leaves.details', string='Leaves Details')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    allocated_leaves = fields.Float('Allocated Leaves', readonly=True)
    used_leaves = fields.Float('Used Leaves', readonly=True)
    remaining_leaves = fields.Float('Remaining Leaves', readonly=True)
    leave_encashment_details_ids = fields.One2many('leave.encashment.details', 'leave_encashment_id')
    updated_leaves = fields.Float('Updated Allocated leaves', readonly=True)
    encashment_leaves = fields.Float('Encashment Leaves', readonly=True)
    encashment_type = fields.Selection([('by_payslip', 'By Payslip'), ('reduse_days', 'Reduce Days'), ('carry_forward', 'Carry Forward Next Year'), ('bank_cash', 'Bank/Cash')], default='by_payslip', required=True)
    journal_id = fields.Many2one('account.journal', string='Payment Method')
    applied_date = fields.Date(string='Encashment Report Date', required=True, default=fields.Date.today)
    year_id = fields.Many2one('year.year', readonly=True)
    is_allocated = fields.Boolean(string="Is Allocated")

    def generate_leave_allowance(self):
        for rec in self:
            ctx = self.env.context
            if not rec.leave_encashment_details_ids:
                raise UserError(_('You need to select Allocation Leave!!'))
            if sum(rec.leave_encashment_details_ids.mapped('encashment_days')) > rec.remaining_leaves:
                raise UserError(_('Encashment Days need to be less than remaining days of %s Employee !!' % rec.employee_id.name))
            elif rec.leave_encashment_details_ids.search([('encashment_days', '=', 0)]):
                raise UserError(_('Encashment Days need to be greater than 0!!'))
            elif not len(rec.leave_encashment_details_ids.mapped('leave_allocation_id').ids) == len(rec.leave_encashment_details_ids):
                raise UserError(_('Leave Allocation need to be different!!'))
            else:
                leave_details_id = rec.leave_details_id
                cutdown_leaves = 0
                encashment_leaves = 0

                if rec.encashment_type == 'carry_forward':
                    if not leave_details_id.annual_leaving_id.allocation_leave_type_id:
                        raise UserError(_('You need to select Allocation leave type for carry forward!!'))

                    for line in rec.leave_encashment_details_ids:
                        if line.leave_allocation_id.number_of_days < line.encashment_days:
                            raise UserError(_('Encashment Days need to be less than Allocation days!!'))
                        allocation_id = self.env['hr.leave.allocation'].search([('id', '=', line.leave_allocation_id.id)])

                        if leave_details_id.annual_leaving_id.is_maximum_leave_carry_forward and leave_details_id.annual_leaving_id.maximum_leave_carry_forward > 0.0 and \
                            (encashment_leaves + line.encashment_days) > leave_details_id.annual_leaving_id.maximum_leave_carry_forward:
                            days = leave_details_id.annual_leaving_id.maximum_leave_carry_forward - encashment_leaves
                            allocation_id.write({'number_of_days': allocation_id.number_of_days - days})
                            rec.updated_leaves = rec.updated_leaves - days
                            leave_details_id.updated_leaves = rec.updated_leaves
                            leave_details_id.encashment_leaves += line.encashment_days
                            encashment_leaves = leave_details_id.annual_leaving_id.maximum_leave_carry_forward
                            self.env['cutdown.leaves.history'].create({'name': 'Leaves Carry Forward',
                                                               'date': datetime.today(),
                                                               'number_of_days': encashment_leaves,
                                                               'leaves_details_id': leave_details_id.id,
                                                               'holiday_status_id': allocation_id.holiday_status_id.id,
                                                               'applied_date': rec.applied_date,
                                                               })
                            break
                        encashment_leaves += line.encashment_days
                        # cutdown_leaves += line.encashment_days
                        allocation_id.write({'number_of_days': allocation_id.number_of_days - line.encashment_days})
                        rec.updated_leaves = rec.updated_leaves - line.encashment_days
                        leave_details_id.updated_leaves = rec.updated_leaves
                        leave_details_id.encashment_leaves += line.encashment_days

                        self.env['cutdown.leaves.history'].create({'name': 'Leaves Carry Forward',
                                                               'date': datetime.today(),
                                                               'number_of_days': line.encashment_days,
                                                               'leaves_details_id': leave_details_id.id,
                                                               'holiday_status_id': allocation_id.holiday_status_id.id,
                                                               'applied_date': rec.applied_date,
                                                               })

                    allocation_obj = self.env['hr.leave.allocation']
                    all_fields = allocation_obj.fields_get()
                    allocation_vals = allocation_obj.default_get(all_fields)
                    allocation_vals.update({'name': 'Carry Forward Leaves Allocation',
                                        'holiday_status_id': leave_details_id.annual_leaving_id.allocation_leave_type_id.id,
                                        'employee_id': leave_details_id.employee_id.id,
                                        'allocation_type': 'regular',
                                        'holiday_type': 'employee',
                                        'number_of_days': encashment_leaves,
                                        'number_of_days_display': encashment_leaves,
                                        })
                    new_allocation_id = self.env['hr.leave.allocation'].create(allocation_vals)
                    new_allocation_id.action_approve()
                    if new_allocation_id and new_allocation_id.holiday_status_id.leave_validation_type == 'both':
                        new_allocation_id.action_validate()

                elif rec.encashment_type == 'by_payslip':
                    cutdown_list = []
                    for line in rec.leave_encashment_details_ids:
                        if line.leave_allocation_id.number_of_days < line.encashment_days:
                            raise UserError(_('Encashment Days need to be less than Allocation days!!'))
                        allocation_id = self.env['hr.leave.allocation'].search([('id', '=', line.leave_allocation_id.id)])
                        allocation_id.write({'number_of_days': allocation_id.number_of_days - line.encashment_days})
                        rec.updated_leaves = rec.updated_leaves - line.encashment_days
                        leave_details_id.updated_leaves = rec.updated_leaves
                        leave_details_id.encashment_leaves += line.encashment_days
                        encashment_leaves += line.encashment_days

                        cutdown_id = self.env['cutdown.leaves.history'].create({'name': 'Leaves Encashment By Payslip',
                                                                               # 'other_hr_payslip_id': other_hr_payslip_id,
                                                                               'date': datetime.today(),
                                                                               'number_of_days': line.encashment_days,
                                                                               'leaves_details_id': leave_details_id.id,
                                                                               'holiday_status_id': allocation_id.holiday_status_id.id,
                                                                               'applied_date': rec.applied_date,
                                                                               }).id
                        cutdown_list.append(cutdown_id)

                    contract_id = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id), ('state', '=', 'open')], limit=1)
                    ded_amount = (contract_id.wage * encashment_leaves / 30)
                    payslip_data = {'employee_id': rec.employee_id.id,
                                    'description': 'Encashment Leave Allowance',
                                    'calc_type': 'amount',
                                    'operation_type': 'allowance',
                                    'amount': ded_amount or 0,
                                    'state': 'done',
                                    }
                    other_hr_payslip_id = self.env['other.hr.payslip'].create(payslip_data).id
                    if cutdown_list:
                        cutdown_ids = self.env['cutdown.leaves.history'].browse(cutdown_list)
                        cutdown_ids.write({'other_hr_payslip_id': other_hr_payslip_id})

                elif rec.encashment_type == 'bank_cash':
                    for line in rec.leave_encashment_details_ids:
                        if line.leave_allocation_id.number_of_days < line.encashment_days:
                            raise UserError(_('Encashment Days need to be less than Allocation days!!'))
                        allocation_id = self.env['hr.leave.allocation'].search([('id', '=', line.leave_allocation_id.id)])
                        allocation_id.write({'number_of_days': allocation_id.number_of_days - line.encashment_days})
                        rec.updated_leaves = rec.updated_leaves - line.encashment_days
                        leave_details_id.updated_leaves = rec.updated_leaves
                        leave_details_id.encashment_leaves += line.encashment_days
                        encashment_leaves += line.encashment_days
                        self.env['cutdown.leaves.history'].create({'name': 'Leaves Encashment By Cash/Bank',
                                                               'date': datetime.today(),
                                                               'number_of_days': line.encashment_days,
                                                               'leaves_details_id': leave_details_id.id,
                                                               'holiday_status_id': allocation_id.holiday_status_id.id,
                                                               'applied_date': rec.applied_date,
                                                               })

                    contract_id = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id), ('state', '=', 'open')], limit=1)
                    amount = (contract_id.wage * encashment_leaves / 30)
                    payment_methods = self.journal_id.outbound_payment_method_ids
                    payment_obj = self.env['account.payment']
                    all_fields = payment_obj.fields_get()
                    account_payment_data = payment_obj.default_get(all_fields)
                    if not rec.employee_id.address_home_id:
                        raise UserError(_("No Home Address found for the employee %s, please configure one.") % (
                            rec.employee_id.name))

                    account_payment_data.update({'payment_method_id': payment_methods and payment_methods[0].id or False,
                                                'payment_type': 'outbound',
                                                'partner_type': 'supplier',
                                                'partner_id': rec.employee_id.address_home_id.id,
                                                'amount': amount,
                                                'journal_id': rec.journal_id.id,
                                                'date': fields.Date.today(),
                                                })
                    payment_id = self.env['account.payment'].create(account_payment_data)
                    payment_id.action_post()
                    leave_details_id.payment_ids = [(4, payment_id.id)]

                else:
                    for line in rec.leave_encashment_details_ids:
                        if line.leave_allocation_id.number_of_days < line.encashment_days:
                            raise UserError(_('Encashment Days need to be less than Allocation days!!'))
                        allocation_id = self.env['hr.leave.allocation'].search([('id', '=', line.leave_allocation_id.id)])
                        allocation_id.write({'number_of_days': allocation_id.number_of_days - line.encashment_days})
                        rec.updated_leaves = rec.updated_leaves - line.encashment_days

                        leave_details_id.updated_leaves = rec.updated_leaves
                        leave_details_id.encashment_leaves += line.encashment_days

                        cutdown_leaves += line.encashment_days

                        self.env['cutdown.leaves.history'].create({'name': 'Leaves Cutdown',
                                                                   'date': datetime.today(),
                                                                   'number_of_days': line.encashment_days,
                                                                   'leaves_details_id': leave_details_id.id,
                                                                   'holiday_status_id': allocation_id.holiday_status_id.id,
                                                                   'applied_date': rec.applied_date,
                                                                   })


class LeaveEncashmentDetails(models.TransientModel):
    _name = 'leave.encashment.details'
    _description = 'Leave Encashment Details'

    leave_encashment_id = fields.Many2one('leave.encashment')
    employee_id = fields.Many2one('hr.employee', related='leave_encashment_id.employee_id')
    leave_allocation_id = fields.Many2one('hr.leave.allocation', required=True, domain=lambda self: self._get_allocation_domain())
    encashment_days = fields.Float('Encashment Days', required=True)
    year_id = fields.Many2one('year.year', related='leave_encashment_id.year_id', store=True, readonly=True)

    def _get_allocation_domain(self):
        domain = []
        ctx = self._context
        year = self.env['year.year'].browse(ctx.get('default_year_id')).code
        allocation_ids = self.env['hr.leave.allocation'].search([
            ('state', '=', 'validate'),
            ('holiday_status_id.is_annual_leave', '=', True),
            ('employee_id', '=', ctx.get('default_employee_id'))])
        types = []
        for allocation in allocation_ids:
            if allocation.holiday_status_id.date_from.year == int(year):
                types.append(allocation.id)
        domain.append(('id', 'in', types))
        return domain
