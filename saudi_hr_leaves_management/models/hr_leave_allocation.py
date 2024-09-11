# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HolidaysAllocation(models.Model):
    """ Allocation Requests Access specifications: similar to leave requests """
    _inherit = "hr.leave.allocation"

    # def _check_approval_update(self, state):
    #     """ Check if target state is achievable. """
    #     current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
    #     is_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
    #     is_manager = self.env.user.has_group('hr_holidays.group_hr_holidays_manager')
    #     is_line_manager = self.env.user.has_group('saudi_hr.group_line_manager')
    #     for holiday in self:
    #         val_type = holiday.holiday_status_id.validation_type
    #         if state == 'confirm':
    #             continue

    #         if state == 'draft':
    #             if holiday.employee_id != current_employee and not is_manager:
    #                 raise UserError(_('Only a Leave Manager can reset other people leaves.'))
    #             continue

    #         if not is_officer:
    #             if not is_line_manager:
    #                 raise UserError(_('Only a Leave Officer or Manager can approve or refuse leave requests.'))

    #         if is_officer:
    #             use ir.rule based first access check: department, members, ... (see security.xml)
    #             holiday.check_access_rule('write')

    #         if holiday.employee_id == current_employee and not is_manager:
    #             raise UserError(_('Only a Leave Manager can approve its own requests.'))

    #         if (state == 'validate1' and val_type == 'both') or (state == 'validate' and val_type == 'manager'):
    #             manager = holiday.employee_id.parent_id or holiday.employee_id.department_id.manager_id
    #             if (manager and manager != current_employee) and not self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
    #                 raise UserError(_('You must be either %s\'s manager or Leave manager to approve this leave') % (holiday.employee_id.name))

    #         if state == 'validate' and val_type == 'both':
    #             if not self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
    #                 raise UserError(_('Only an Leave Manager can apply the second approval on leave requests.'))

    def action_confirm(self):
        """
            Overwrite Base method for check one time allocation of leave.
            :return: res
        """
        if self.filtered(lambda holiday: holiday.state != 'draft'):
            raise UserError(_('Leave request must be in Draft state ("To Submit") in order to confirm it.'))

        for holiday in self:
            if holiday.holiday_status_id.one_time_usable:
                leave_request_ids = self.env['hr.leave'].search_count([
                    ('employee_id', '=', holiday.employee_id.id),
                    ('holiday_status_id', '=', self.holiday_status_id.id),
                    ('state', 'in', ['confirm', 'validate1', 'validate'])])
                leave_allocation_request_ids = self.env['hr.leave.allocation'].search_count([
                    ('employee_id', '=', holiday.employee_id.id),
                    ('holiday_status_id', '=', self.holiday_status_id.id),
                    ('state', 'in', ['confirm', 'validate1', 'validate'])])
                if leave_request_ids or leave_allocation_request_ids:
                    raise UserError(_('%s is already assign or used by %s.') % (holiday.holiday_status_id.name,
                                                                                holiday.employee_id.name))

        res = self.write({'state': 'confirm'})
        self.activity_update()
        return res
