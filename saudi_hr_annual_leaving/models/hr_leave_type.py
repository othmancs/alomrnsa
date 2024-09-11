# -*- coding: utf-8 -*-
# Part of odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class HolidaysType(models.Model):
    _inherit = 'hr.leave.type'

    def annual_leave_get_days(self, employee_id, date_start, date_stop):
        annual_leave_requests = self.env['hr.leave'].search([
            ('employee_id', '=', employee_id),
            ('state', 'in', ['validate']), #'confirm', 'validate1',
            ('holiday_status_id', 'in', self.ids),
            ('request_date_from', '>=', date_start),
            ('request_date_to', '<=', date_stop)
        ])

        allocations = self.env['hr.leave.allocation'].search([
            ('employee_id', '=', employee_id),
            ('state', 'in', ['validate']), # 'confirm', 'validate1',
            ('holiday_status_id', 'in', self.ids)
        ])
        result = dict((id, dict(max_leaves=0, leaves_taken=0, remaining_leaves=0, virtual_remaining_leaves=0)) for id in self.ids)

        for request in annual_leave_requests:
            status_dict = result[request.holiday_status_id.id]
            status_dict['leaves_taken'] += request.number_of_days
            status_dict['remaining_leaves'] -= request.number_of_days

        holiday_status_list = []
        for allocation in allocations:
            status_dict = result[allocation.holiday_status_id.id]
            status_dict['virtual_remaining_leaves'] += allocation.number_of_days
            status_dict['max_leaves'] += allocation.number_of_days
            status_dict['remaining_leaves'] += allocation.number_of_days

            if allocation.holiday_status_id.id not in holiday_status_list:
                holiday_status_list.append(allocation.holiday_status_id.id)

        leaves_details_ids = self.env['leaves.details'].search([('employee_id', '=', employee_id),
                                                    ('year_id.date_start', '>=', date_start),
                                                    ('year_id.date_stop', '<=', date_stop)])

        # for holiday_status_id in self.env['hr.leave.type'].browse(holiday_status_list):
        #     status_dict = result[holiday_status_id.id]
        #     for leave in leaves_details_ids:
        #         encashment_days = sum(leave.cutdown_leaves_history_ids.filtered(lambda l: l.holiday_status_id.id == holiday_status_id.id and l.applied_date and \
        #                             (l.applied_date >= holiday_status_id.validity_start and l.applied_date <= holiday_status_id.validity_stop)).mapped('number_of_days'))
        #         status_dict['max_leaves'] += encashment_days
        #         status_dict['leaves_taken'] += encashment_days

        return result

    def leave_get_days(self, employee_id, date_start, date_stop):
        # need to use `dict` constructor to create a dict per id
        result = dict((id, dict(max_leaves=0, leaves_taken=0, remaining_leaves=0, virtual_remaining_leaves=0)) for id in self.ids)

        requests = self.env['hr.leave'].search([
            ('employee_id', '=', employee_id),
            ('state', 'in', ['validate']), # 'confirm', 'validate1',
            ('holiday_status_id', 'in', self.ids),
            ('request_date_from', '>=', date_start),
            ('request_date_to', '<=', date_stop)
        ])

        allocations = self.env['hr.leave.allocation'].search([
            ('employee_id', '=', employee_id),
            ('state', 'in', ['validate']), # 'confirm', 'validate1',
            ('holiday_status_id', 'in', self.ids)
        ])

        for request in requests:
            status_dict = result[request.holiday_status_id.id]
            status_dict['virtual_remaining_leaves'] -= request.number_of_days
            status_dict['leaves_taken'] += request.number_of_days
            status_dict['remaining_leaves'] -= request.number_of_days

        for allocation in allocations.sudo():
            status_dict = result[allocation.holiday_status_id.id]
            status_dict['virtual_remaining_leaves'] += allocation.number_of_days
            status_dict['max_leaves'] +=  allocation.number_of_days
            status_dict['remaining_leaves'] += allocation.number_of_days
        return result
