# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import pytz

from datetime import datetime, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT


class PublicHolidays(models.Model):
    _name = 'hr.holidays.public'
    _description = 'Public Holidays'
    _order = "name"

    name = fields.Char("Name", required=True)
    state = fields.Selection([('draft', 'Draft'), ('open', 'Open'), ('close', 'Close'), ('cancel', 'Cancel')],
                             string="Status", required=True, default='draft')
    line_ids = fields.One2many('hr.holidays.public.line', 'holidays_id', 'Holiday Dates')
    year_id = fields.Many2one('year.year', 'Year', required=True, ondelete='cascade')
    company_id = fields.Many2one('res.company', 'Company', required=True)
    resource_ids = fields.Many2many('resource.calendar', 'rel_public_holidays_calendar', 'public_leave_id',
                                    'calendar_id', 'Resource', required=False)

    @api.depends('name', 'year_id')
    def name_get(self):
        """
            Name get combination of `Name` and `Year name`
        """
        res = []
        for holiday in self:
            name = " - ".join([holiday.name, holiday.year_id.name or ''])
            res.append((holiday.id, name))
        return res

    def unlink(self):
        """
            remove/ delete existing record if holiday state not in close.
        """
        for holiday in self.filtered(lambda holiday: holiday.state in ['close']):
            raise UserError(_('You cannot remove the record which is in %s state!') % holiday.state)
        return super(PublicHolidays, self).unlink()

    def set_to_draft(self):
        """
            Set the holiday is in close state.
        """
        self.ensure_one()
        self.state = 'draft'

    def set_to_close(self):
        """
            Set the holiday is in close state.
        """
        self.ensure_one()
        self.state = 'close'

    def set_to_open(self):
        """
            Set the holiday is in open state.
        """
        def get_planned_attendance(work_hours, weekday):
            planned_check_in, planned_check_out = [], []
            for wo in work_hours:
                if str(weekday) == wo[2].get('dayofweek'):
                    planned_check_in.append(wo[2].get('hour_from')) if wo[2].get('hour_from') else False
                    planned_check_out.append(wo[2].get('hour_to')) if wo[2].get('hour_to') else False
            return {
                'planned_check_in': min(planned_check_in) if planned_check_in != [] else False,
                'planned_check_out': max(planned_check_out) if planned_check_out != [] else False
            }

        self.ensure_one()
        calendar_leave_obj = self.env['resource.calendar.leaves']
        for resource in self.resource_ids:
            working_hours = resource.default_get('attendance_ids')['attendance_ids']
            for holiday in self.line_ids:
                tz_offset = datetime.now(pytz.timezone(resource.tz or 'GMT')).utcoffset()
                date_from_time = timedelta(hours=get_planned_attendance(working_hours, holiday.start_date.weekday()).get('planned_check_in'))
                date_to_time = timedelta(hours=get_planned_attendance(working_hours, holiday.end_date.weekday()).get('planned_check_out') or 23.99)
                calendar_leave_obj.create({'name': holiday.name, 'calendar_id': resource.id,
                                           'time_type': 'leave',
                                           'date_from': datetime.combine(holiday.start_date, ((datetime.min + date_from_time) - tz_offset).time()).strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                           'date_to': datetime.combine(holiday.end_date, ((datetime.min + date_to_time) - tz_offset).time()).strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                           'public_line_id': holiday.id})
        self.state = 'open'

    def set_to_cancel(self):
        """
            Set to cancel.
        """
        self.ensure_one()
        calendar_leave_obj = self.env['resource.calendar.leaves']
        calendar_leave_ids = calendar_leave_obj.search([('public_line_id', 'in', self.line_ids.ids)])
        calendar_leave_ids.unlink()
        self.state = 'cancel'


class PublicHolidaysLine(models.Model):
    _name = 'hr.holidays.public.line'
    _description = 'Public Holidays Lines'
    _order = "start_date, name desc"

    name = fields.Char('Name', size=128, required=True)
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    holidays_id = fields.Many2one('hr.holidays.public', 'Holiday Calendar Year', ondelete="cascade")

    _sql_constraints = [
        ('date_check', "CHECK (start_date <= end_date)", "The start date must be anterior to the end date."),
    ]

    @api.constrains('start_date', 'end_date')
    def check_date_from_to(self):
        """
            Constraints for the holiday is overlaps on same day or not.
        """
        for record in self:
            nworking = self.search_count([('start_date', '<=', record.end_date), ('end_date', '>=', record.start_date),
                                          ('holidays_id', '=', record.holidays_id.id), ('id', '!=', record.id)])
            if nworking:
                raise ValidationError(_('You can not have holiday that overlaps on same days!'))
