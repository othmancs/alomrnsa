# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, exceptions, _


class LeaveDetailsReport(models.Model):
    _name = "leaves.details.report"
    _description = 'Leaves Details Summary / Report'
    _auto = False
    _order = "employee_id"

    employee_id = fields.Many2one('hr.employee', string="Employee", readonly=True)
    department_id = fields.Many2one('hr.department', 'Department', readonly=True)
    allocated_leaves = fields.Float('Allocated Leaves', readonly=True)
    used_leaves = fields.Float('Used Leaves', readonly=True)
    remaining_leaves = fields.Float('Remaining Leaves', readonly=True)
    leave_type = fields.Selection([
        ('allocation', 'Allocation Request'),
        ('request', 'Time Off Request')
        ], string='Request Type', readonly=True)
    holiday_status_id = fields.Many2one("hr.leave.type", string="Leave Type", readonly=True)
    date_from = fields.Datetime('Start Date', readonly=True)
    date_to = fields.Datetime('End Date', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW leaves_details_report as
            (SELECT row_number() over(ORDER BY leaves.employee_id) as id,
                    leaves.employee_id as employee_id,
                    leaves.department_id as department_id,
                    leaves.allocated_leaves as allocated_leaves,
                    leaves.used_leaves as used_leaves,
                    leaves.remaining_leaves as remaining_leaves,
                    leaves.holiday_status_id as holiday_status_id,
                    leaves.date_from as date_from,
                    leaves.date_to as date_to,
                    leaves.leave_type as leave_type
                    from (select
                        allocation.employee_id as employee_id,
                        allocation.department_id as department_id,
                        allocation.number_of_days as allocated_leaves,
                        null as used_leaves,
                        allocation.number_of_days as remaining_leaves,
                        allocation.holiday_status_id as holiday_status_id,
                        null as date_from,
                        null as date_to,
                        'allocation' as leave_type
                        from hr_leave_allocation as allocation
                        UNION ALL select
                        request.employee_id as employee_id,
                        request.department_id as department_id,
                        null as allocated_leaves,
                        request.number_of_days as used_leaves,
                        (request.number_of_days * -1) as remaining_leaves,
                        request.holiday_status_id as holiday_status_id,
                        request.date_from as date_from,
                        request.date_to as date_to,
                        'request' as leave_type
                        from hr_leave as request) leaves
            );
            """)