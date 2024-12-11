# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrEndOfService(models.Model):
    _inherit = 'hr.end.service'

    remaining_balance_time_off = fields.Float(string="Remaining balance", compute='_compute_remaining_time_off',
                                              stote=True, readonly=True)

    remaining_balance_time_off_amount = fields.Float(string="Remaining balance Amount",
                                                     compute='_compute_remaining_time_off', stote=True, readonly=True)

    @api.depends("employee_id")
    def _compute_remaining_time_off(self):
        leave_allocation_obj = self.env["hr.leave.allocation"]
        leave_obj = self.env["hr.leave"]
        domain = [('state', '=', 'validate'), ('holiday_status_id.is_include_balance', '=', True)]
        for end_service in self:
            # get number of allocations for employee
            leave_allocation_ids = leave_allocation_obj.search(
                domain + [('employee_id', '=', end_service.employee_id.id)])
            number_allocations_days = sum(allocation.number_of_days for allocation in leave_allocation_ids)

            # get number of request leaves for employee
            request_leave_ids = leave_obj.search(domain + [('employee_id', '=', end_service.employee_id.id)])
            number_request_leaves = sum(request_leave.number_of_days for request_leave in request_leave_ids)

            end_service.remaining_balance_time_off = number_allocations_days - number_request_leaves

            end_service.remaining_balance_time_off_amount = end_service.remaining_balance_time_off * end_service.contract_id.wage_day
