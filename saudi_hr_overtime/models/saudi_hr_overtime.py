# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, api, models, _
from datetime import timedelta
from pytz import utc, timezone
from collections import defaultdict
from odoo.exceptions import UserError


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    overtime_hours = fields.Float('Overtime Hours', compute='compute_overtime', store=True)
    duration = fields.Float(compute='get_attendance_duration', store=True, string="Attendance duration")

    @api.depends('check_in', 'check_out')
    def get_attendance_duration(self):
        for rec in self:
            if rec.check_out:
                total_difference = (rec.check_out - rec.check_in).total_seconds() / 3600
                rec.duration = total_difference
            else:
                rec.duration = 0.0


    # Put this method in comment because of there is no use for payroll
    # def float_time_convert(self, float_val):
    #     """
    #         Convert float value into time.
    #     """
    #     hours = math.floor(abs(float_val))
    #     mins = abs(float_val) - hours
    #     mins = round(mins * 60)
    #     if mins >= 60.0:
    #         hours = hours + 1
    #         mins = 0.0
    #     float_time = '%02d:%02d' % (hours, mins)
    #     return float_time

    @api.depends('check_out', 'check_in')
    def compute_overtime(self):
        """
            Calculate employee overtime hours
        """
        for rec in self:
            if rec.check_out:
                total_difference = (rec.check_out - rec.check_in).total_seconds() / 3600
                active_contract_ids = self.env['hr.employee'].browse(rec.employee_id.id)._get_contracts(rec.check_in, rec.check_in, states=['open'])
                if active_contract_ids and active_contract_ids[0].calculate_overtime:
                    resource_calendar_id = active_contract_ids[0].resource_calendar_id
                    working_hours = resource_calendar_id.default_get('attendance_ids')['attendance_ids']
                    weekday_list = []
                    for weekday in working_hours:
                        if weekday[2].get('dayofweek') not in weekday_list:
                            weekday_list.append(weekday[2].get('dayofweek'))
                    # [Cathy: change beacuse of type is different]
                    if str(rec.check_in.weekday()) not in weekday_list:
                        rec.overtime_hours = total_difference

                    # native datetimes are made explicit in UTC
                    if not rec.check_in.tzinfo:
                        from_datetime = rec.check_in.replace(tzinfo=utc)
                    if not rec.check_out.tzinfo:
                        to_datetime = rec.check_out.replace(tzinfo=utc)
                    # total hours per day: retrieve attendances with one extra day margin,
                    # in order to compute the total hours on the first and last days
                    if not rec.env.user.tz:
                        raise UserError(_("Add user timezone first!!"))
                    from_datetime = from_datetime.astimezone(timezone(rec.env.user.tz))
                    to_datetime = to_datetime.astimezone(timezone(rec.env.user.tz))

                    from_full = from_datetime - timedelta(days=1)
                    to_full = to_datetime + timedelta(days=1)
                    intervals = resource_calendar_id._attendance_intervals_batch(from_full, to_full, resource_calendar_id)[resource_calendar_id.id]
                    day_total = defaultdict(float)
                    for start, stop, meta in intervals:
                        if from_datetime.date() == start.date() and to_datetime.date() == stop.date():
                            day_total[start.date()] = (stop - start).total_seconds() / 3600
                            overtime_hours = total_difference - list(day_total.values())[0]
                            if overtime_hours > 0:
                                rec.overtime_hours = overtime_hours
                            else:
                                rec.overtime_hours = 0.0


class HrContract(models.Model):
    _inherit = "hr.contract"

    calculate_overtime = fields.Boolean('Calculate Overtime', default=False)
    overtime_limit = fields.Float('Overtime Limit Hours', default=False)
    weekend_overtime = fields.Boolean('Weekend\'s Overtime', default=False)
    public_holiday_overtime = fields.Boolean('Public Holiday\'s Overtime', default=False)
    weekend_overtime_rate = fields.Float('Overtime Rate', default=1.5, help="Weekend overtime rate")
    working_day_overtime_rate = fields.Float('Overtime Rate', default=1.5, help="Normal working day overtime rate")
    public_holiday_overtime_rate = fields.Float('Overtime Rate', default=1.5, help="Public holiday's overtime rate")

    @api.onchange('calculate_overtime')
    def onchange_calculate_overtime(self):
        self.weekend_overtime = False
        self.public_holiday_overtime = False
        if self.calculate_overtime:
            self.weekend_overtime = True
            self.public_holiday_overtime = True