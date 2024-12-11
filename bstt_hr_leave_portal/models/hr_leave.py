# -*- coding: utf-8 -*-
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from pytz import timezone, UTC, utc
from odoo.tools import format_datetime
from odoo.tools import format_time
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    def _get_default_employee_id(self):
        employee_id = self.env.user.employee_id
        return employee_id.id if employee_id else False

    def _get_remaining_leaves(self):
        employee_id = self._get_default_employee_id()
        holiday_status_id = self.env['hr.leave.type'].search([], order='sequence', limit=1)

        if not employee_id or not holiday_status_id or holiday_status_id.requires_allocation == 'no':
            return False

        mapped_days = holiday_status_id.get_employees_days([employee_id], date.today())
        leave_days = mapped_days[employee_id][holiday_status_id.id]
        remaining_leaves = leave_days['remaining_leaves']
        return remaining_leaves

    employee_id = fields.Many2one(default=_get_default_employee_id)
    remaining_leaves = fields.Float(default=_get_remaining_leaves)

    @api.onchange('employee_id', 'holiday_status_id')
    def _check_remaining_leaves(self):
        for holiday in self:
            if holiday.holiday_type != 'employee' or not holiday.employee_id or not holiday.holiday_status_id or holiday.holiday_status_id.requires_allocation == 'no':
                continue
            mapped_days = holiday.holiday_status_id.get_employees_days([holiday.employee_id.id], holiday.date_from)
            leave_days = mapped_days[holiday.employee_id.id][holiday.holiday_status_id.id]
            holiday.remaining_leaves = leave_days['remaining_leaves'] if 'remaining_leaves' in leave_days else 0
