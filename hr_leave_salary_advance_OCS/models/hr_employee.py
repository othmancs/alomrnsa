from odoo import models, api
from odoo.exceptions import UserError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _get_remaining_leaves(self, leave_type):
        self.ensure_one()
        allocations = self.env['hr.leave.allocation'].search([
            ('employee_id', '=', self.id),
            ('holiday_status_id', '=', leave_type.id),
            ('state', '=', 'validate')
        ])
        return sum(allocations.mapped('number_of_days_display'))

    def _deduct_leaves(self, leave_type, days):
        self.ensure_one()
        allocations = self.env['hr.leave.allocation'].search([
            ('employee_id', '=', self.id),
            ('holiday_status_id', '=', leave_type.id),
            ('state', '=', 'validate')
        ], order='id desc')

        if not allocations:
            raise UserError("لا يوجد تخصيص إجازة للموظف")

        remaining_days = days
        for allocation in allocations:
            if remaining_days <= 0:
                break
            if allocation.number_of_days_display >= remaining_days:
                allocation.number_of_days_display -= remaining_days
                remaining_days = 0
            else:
                remaining_days -= allocation.number_of_days_display
                allocation.number_of_days_display = 0

        if remaining_days > 0:
            raise UserError("رصيد الإجازة غير كافي للخصم")