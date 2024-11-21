from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, time, timedelta
from pytz import timezone
import logging
_logger = logging.getLogger(__name__)

class HrOvertime(models.Model):
    _inherit = 'hr.overtime'

    leave_type = fields.Many2one('hr.leave.type', string='Leave Type',
                                 domain=[('name', '!=', 'Extra Hours')])
    office_hours_start = fields.Float(string='Office Hours Start', default=9.0)
    office_hours_end = fields.Float(string='Office Hours End', default=17.0)
    days_difference = fields.Float(string="Days Difference", compute='_compute_days_difference', store=True)
    work_done_date = fields.Date(string="Work Done Date", compute='_compute_work_done_date', store=True)
    today_date = fields.Date(string="Today's Date", default=fields.Date.today)



    @api.depends('date_from', 'date_to')
    def _compute_work_done_date(self):
        for record in self:
            record.work_done_date = record.date_from.date() if record.date_from else False

    @api.depends('work_done_date')
    def _compute_days_difference(self):
        for record in self:
            if record.work_done_date:
                record.days_difference = self._get_working_days_between(record.work_done_date, fields.Date.today())

    def _get_working_days_between(self, start_date, end_date):
        """Calculate the number of working days between two dates."""
        calendar = self.env.company.resource_calendar_id or self.env['resource.calendar'].search([], limit=1)
        if not calendar:
            raise UserError(_("No working time calendar found. Please set one on the company."))

        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        return calendar.get_work_duration_data(start_datetime, end_datetime)['days']

    @api.constrains('date_from', 'date_to', 'days_no_tmp')
    def _check_overtime_conditions(self):
        for record in self:
            duration = record.days_no_tmp
            if duration < 2:
                raise ValidationError("Extra hours must be at least 2 hours.")

            user_tz = timezone(self.env.user.tz or 'UTC')
            start_datetime = record.date_from.astimezone(user_tz)
            end_datetime = record.date_to.astimezone(user_tz)

            # Calculate office hours for the start date
            start_date = start_datetime.date()
            office_start = user_tz.localize(
                datetime.combine(start_date, self._float_to_time(record.office_hours_start)))
            office_end = user_tz.localize(datetime.combine(start_date, self._float_to_time(record.office_hours_end)))

            _logger.info(f"Localized start: {start_datetime}")
            _logger.info(f"Localized end: {end_datetime}")
            _logger.info(f"Localized office start: {office_start}")
            _logger.info(f"Localized office end: {office_end}")

            # Perform your checks here using the localized times
            if not (end_datetime <= office_start or start_datetime >= office_end):
                raise ValidationError(
                    _("Overtime should be entirely outside office hours (before {} or after {}).".format(
                        office_start.strftime("%I:%M %p"),
                        office_end.strftime("%I:%M %p"))))

            work_done_date = start_datetime.date()
            today = fields.Date.today()
            working_days_difference = self._get_working_days_between(work_done_date, today)

            if working_days_difference > 2:
                raise ValidationError(
                    _("Extra hours claim must be made within 2 working days from the date of work done."))

    @api.model
    def _float_to_time(self, float_time):
        hours, minutes = divmod(float_time * 60, 60)
        return time(int(hours), int(minutes))

    @api.onchange('date_from', 'date_to', 'days_no_tmp')
    def _onchange_check_extra_hours(self):
        # This method can be used to provide warnings in the UI before saving
        pass






# from calendar import calendar
#
# from odoo import api, fields, models, _
# from odoo.exceptions import UserError
# from datetime import datetime, timedelta, time
# from pytz import UTC
# import pytz
# UTC = pytz.UTC
# from odoo.exceptions import ValidationError




# class HrCustomLeave(models.Model):
#     _inherit = 'hr.overtime'
#
#     type = fields.Selection(
#         string='Leave Type',
#         required=True,
#         domain=[('name', '!=', 'Extra Hours')]
#     )
#     office_hours_start = fields.Float(string='Office Hours Start', default=9.0)  # 9:00 AM
#     office_hours_end = fields.Float(string='Office Hours End', default=17.0)
#     days_difference = fields.Float(string="days difference",compute='_get_working_days_between')
#     work_done_date = fields.Datetime(string="date" ,compute='_get_working_days_between')
#     today_date = fields.Datetime(string="todays Date", default = datetime.today())
#
#
#
#
#     @api.onchange('date_from', 'date_to', 'days_no_tmp')
#     def _onchange_check_extra_hours(self):
#             if self.date_from and self.date_to and self.days_no_tmp:
#                 try:
#
#                     duration = self.days_no_tmp
#                     # Check duration
#                     if duration < 2:
#                         return {'warning': {
#                             'title': "Invalid Extra Hours",
#                             'message': "Extra hours must be at least 2 hours."
#                         }}
#                     start_datetime = fields.Datetime.from_string(self.date_from)
#                     end_datetime = fields.Datetime.from_string(self.date_to)
#                     start_time = start_datetime.time()
#                     end_time = end_datetime.time()
#                     start_date = start_datetime.date()
#
#                     office_start = time(9, 0)  # 9:00 AM
#                     office_end = time(17, 0)  # 5:00 PM
#
#                     if (office_start <= start_time <= office_end) or \
#                             (office_start <= end_time <= office_end):
#                         return {'warning': {
#                             'title': _("Warning"),
#                             'message': _("Overtime should be outside office hours (before 9 AM or after 5 PM).")
#                         }}
#
#                     # Check if claim is within 2 working days
#                     today = fields.Date.today()
#                     work_done_date = start_date
#
#                     # calendar_id = self.employee_id.resource_calendar_id
#                     # start_date = min(work_done_date, today)
#                     # end_date = max(work_done_date, today)
#                     # if not calendar_id:
#                     #     raise UserError("Calendar ID is not defined for the employee")
#                     days_difference = self._get_working_days_between(work_done_date, today)
#
#                     if days_difference > 2:
#                         return {'warning': {
#                             'title': "Late Claim",
#                             'message': "Extra hours claim must be made within 2 working days from the date of work done."
#                         }}
#                     self.days_difference = days_difference
#
#
#
#                 except ValueError:
#                     return {'warning': {
#                         'title': "Invalid Time Format",
#                         'message': "Please enter valid time values."
#                     }}
#
#             # elif self.request_hour_from or self.request_hour_to:
#             #     return {'warning': {
#             #         'title': "Incomplete Time Entry",
#             #         'message': "Please specify both start and end times for Extra Hours."
#             #     }}
#
#     # @api.constrains('date_from', 'date_to', 'days_no_tmp')
#     # def _check_extra_hours(self):
#     #     for record in self:
#     #             if record.date_from and record.date_to and record.days_no_tmp:
#     #                 try:
#     #
#     #                     duration = record.days_no_tmp
#     #
#     #                     if duration < 2:
#     #                         raise ValidationError("Extra hours must be at least 2 hours.")
#     #
#     #                     start_time = fields.Datetime.from_string(self.date_from).time()
#     #                     end_time = fields.Datetime.from_string(self.date_to).time()
#     #                     start_date = fields.Datetime.from_string(self.date_from).date()
#     #
#     #                     office_start = time(9, 0)  # 9:00 AM
#     #                     office_end = time(17, 0)  # 5:00 PM
#     #
#     #                     if not (start_time <= office_start or start_time >= office_end) or \
#     #                             not (end_time <= office_start or end_time >= office_end):
#     #                         raise ValidationError("Extra hours must be outside office hours(before 9am or after 5pm")
#     #
#     #                     today = fields.Date.today()
#     #                     work_done_date = start_date
#     #                     days_difference = self._get_working_days_between(work_done_date, today)
#     #                     if days_difference > 2:
#     #                         raise UserError(
#     #                             "Extra hours claim must be made within 2 working days from the date of work done.")
#     #
#     #                 except ValueError:
#     #                     raise UserError("Please enter valid time values.")
#
#     def _get_working_days_between(self, work_done_date, today):
#         """Calculate the number of working days between two dates."""
#         current_date = work_done_date
#         working_days = 0
#         while current_date <= today:
#             if current_date.weekday() < 5:  # Monday = 0, Friday = 4
#                 working_days += 1
#             current_date += timedelta(days=1)
#             self.work_done_date = work_done_date
#             self.today_date = today
#         return working_days

    # def _get_working_days_between(self, start_date, end_date, calendar_id, public_holidays=None, work_days=None):
    #     """Calculate the number of working days between two dates."""
    #
    #     if public_holidays is None:
    #         domain = [
    #             ('calendar_id', '=', calendar_id.id),
    #             ('resource_id', '=', False),  # Global leaves (holidays)
    #             ('date_from', '<=', end_date),
    #             ('date_to', '>=', start_date),
    #         ]
    #         public_holidays = self.env['resource.calendar.leaves'].search(domain)
    #
    #     if work_days is None:
    #         work_days = [0, 1, 2, 3, 4]  # Monday to Friday
    #
    #     current_date = start_date
    #     working_days = 0
    #     while current_date <= end_date:
    #         if current_date.weekday() in work_days and not any(
    #                 holiday.date_from.date() <= current_date <= holiday.date_to.date() for holiday in public_holidays
    #         ):
    #             working_days += 1
    #         else:
    #             current_date += timedelta(days=1)
    #
    #     return working_days

    # def _get_working_days_between(self, start_date, end_date, calendar_id=None):
    #     """Calculate the number of working days between two dates based on the resource calendar."""
    #     self.ensure_one()
    #
    #     if not calendar_id:
    #         calendar_id = self.env.company.resource_calendar_id
    #
    #     if not isinstance(calendar_id, self.env['resource.calendar'].__class__):
    #         calendar_id = self.env['resource.calendar'].browse(calendar_id)
    #
    #     # Ensure dates are in UTC and at the start of the day
    #     start_date = start_date.replace(tzinfo=UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    #     end_date = end_date.replace(tzinfo=UTC).replace(hour=23, minute=59, second=59, microsecond=999999)
    #
    #     # Fetch public holidays
    #     domain = [
    #         ('calendar_id', '=', calendar_id.id),
    #         ('resource_id', '=', False),  # Global leaves (holidays)
    #         ('date_from', '<=', end_date),
    #         ('date_to', '>=', start_date),
    #     ]
    #     public_holidays = self.env['resource.calendar.leaves'].search(domain)
    #
    #     # Calculate working days
    #     working_days = 0
    #     current_date = start_date
    #     while current_date <= end_date:
    #         # Check if it's a working day according to the calendar
    #         if calendar_id.is_working_day(current_date):
    #             # Check if it's not a public holiday
    #             if not any(holiday.date_from <= current_date <= holiday.date_to for holiday in public_holidays):
    #                 working_days += 1
    #         current_date += timedelta(days=1)
    #
    #     return working_days
    # def _get_working_days_between(self, start_date, end_date, calendar_id):
    #     self.ensure_one()
    #
    #     if not calendar_id:
    #         calendar_id = self.env.company.resource_calendar_id
    #
    #     if not isinstance(calendar_id, self.env['resource.calendar'].__class__):
    #         calendar_id = self.env['resource.calendar'].browse(calendar_id)
    #
    #     if isinstance(start_date, datetime):
    #         start_date = start_date.replace(tzinfo=pytz.UTC, hour=0, minute=0, second=0, microsecond=0)
    #     else:
    #         start_date = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=pytz.UTC)
    #
    #     if isinstance(end_date, datetime):
    #         end_date = end_date.replace(tzinfo=pytz.UTC, hour=0, minute=0, second=0, microsecond=0)
    #     else:
    #         end_date = datetime.combine(end_date, datetime.min.time()).replace(tzinfo=pytz.UTC)
    #
    #     # Fetch public holidays
    #     domain = [
    #         ('calendar_id', '=', calendar_id.id),
    #         ('resource_id', '=', False),  # Global leaves (holidays)
    #         ('date_from', '<=', end_date),
    #         ('date_to', '>=', start_date),
    #     ]
    #     public_holidays = self.env['resource.calendar.leaves'].search(domain)
    #
    #     # Fetch working days from calendar attendance
    #     attendance_days = self.env['resource.calendar.attendance'].search([
    #         ('calendar_id', '=', calendar_id.id)
    #     ])
    #
    #     def is_working_day(date):
    #         day_of_week = str(date.weekday())
    #         for attendance in attendance_days:
    #             if attendance.dayofweek == day_of_week:
    #                 return True
    #         return False
    #
    #     # Calculate working days
    #     working_days = 0
    #     current_date = start_date
    #     while current_date <= end_date:
    #         # Check if it's a working day according to the calendar
    #         if is_working_day(current_date):
    #             # Check if it's not a public holiday
    #             if not any(holiday.date_from.date() <= current_date <= holiday.date_to.date() for holiday in public_holidays):
    #                 working_days += 1
    #         current_date += timedelta(days=1)
    #
    #     return working_days
