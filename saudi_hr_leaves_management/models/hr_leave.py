# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import math
from datetime import datetime, timedelta, date, time
from pytz import utc, timezone
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.resource.models.resource import HOURS_PER_DAY
from dateutil.relativedelta import relativedelta


class LeaveDetail(models.Model):
    _name = "leave.detail"
    _description = "Leave Details"

    name = fields.Char(string="Month")
    period_id = fields.Many2one('year.period', string="Month")
    leave_id = fields.Many2one('hr.leave', string="Holiday")
    already_taken = fields.Float(string="Already Taken")
    already_taken_month = fields.Float(string="Already Taken in current Month")
    paid_leave = fields.Float(string="Paid Leave")
    unpaid_leave = fields.Float(string="Unpaid Leave")
    leave_hours = fields.Float(string="Paid Leave Hours")
    total_leave_hours = fields.Float(string="Total Leave Hours")
    unpaid_leave_hours = fields.Float(string="Unpaid Leave Hours")
    total_leave = fields.Float(string="Total Leave")


class HolidaysRequest(models.Model):
    _inherit = "hr.leave"

    @api.depends('number_of_days')
    def _compute_number_of_hours_display(self):
        for holiday in self:
            calendar = holiday.employee_id.resource_calendar_id or self.env.user.company_id.resource_calendar_id
            if holiday.date_from and holiday.date_to:
                if holiday.holiday_status_id and not holiday.holiday_status_id.skip and not holiday.request_unit_half and not holiday.request_unit_hours:
                    holiday.number_of_hours_display = (holiday.number_of_days * HOURS_PER_DAY)
                else:
                    number_of_hours = calendar.get_work_hours_count(holiday.date_from, holiday.date_to)
                    holiday.number_of_hours_display = number_of_hours or (holiday.number_of_days * HOURS_PER_DAY)
            else:
                holiday.number_of_hours_display = 0

    @api.model
    def isWorkingDay(self, holiday_date, employee_id=False, contract_ids=[]):
        """
            Check holiday date is working day
        """
        weekday_list = []
        if employee_id and contract_ids:
            resource_calendar_id = contract_ids[0].resource_calendar_id
            working_hours = resource_calendar_id.default_get('attendance_ids')['attendance_ids']
            for weekday in working_hours:
                if weekday[2].get('dayofweek') not in weekday_list:
                    weekday_list.append(weekday[2].get('dayofweek'))
        if not str(holiday_date.weekday()) in weekday_list:
            return False
        return True

    @api.model
    def isweekend(self, date=False, contract=False):
        working_days = list(set(contract.resource_calendar_id.attendance_ids.mapped('dayofweek')))
        working_days = [int(i) for i in working_days]
        if date.weekday() not in list(set(working_days)):
            return True
        return False

    @api.model
    def isPublicDay(self, holiday_date, employee_id=False, fiscalyear=False):
        """
            Check holiday date is public day
        """
        if holiday_date and fiscalyear:
            public_holi_line_obj = self.env['hr.holidays.public.line']
            period_id = self.env['year.period'].find(dt=holiday_date.date(), fiscalyear_id=fiscalyear.id, exception=True)
            holiday_date = datetime.combine(holiday_date, datetime.min.time())
            if period_id and period_id.date_start:
                holidays_line_ids = public_holi_line_obj.search([('holidays_id.year_id', '=', fiscalyear.id),
                                                                 ('holidays_id.state', '=', 'open')])
                for line_obj in holidays_line_ids:
                    if holiday_date >= datetime.combine(line_obj.start_date, datetime.min.time()) and holiday_date <= datetime.combine(line_obj.end_date, datetime.min.time()):
                        return True
        return False

    leave_details = fields.One2many('leave.detail', 'leave_id', string="Leave Details", copy=False)
    notes = fields.Text(string='Notes')

    @api.onchange('holiday_status_id')
    def _onchange_holiday_status_id(self):
        #super(HolidaysRequest, self)._onchange_holiday_status_id()
        self.notes = False
        if self.holiday_status_id:
            self.notes = self.holiday_status_id.notes

    def _get_number_of_days(self, date_from, date_to, employee_id):
        res = super(HolidaysRequest, self)._get_number_of_days(date_from, date_to, employee_id)
        if employee_id and self.holiday_status_id and not self.holiday_status_id.skip and not self.request_unit_half and not self.request_unit_hours:
            time_delta = date_to - date_from
            days = math.ceil(time_delta.days + float(time_delta.seconds) / 86400)
            res.update({'days': math.ceil(time_delta.days + float(time_delta.seconds) / 86400),
                        'hours': days * HOURS_PER_DAY})
        return res

    def get_fiscal_year(self, fiscal_date=False):
        if not fiscal_date:
            fiscal_date = fields.Date.today()
        for rec in self:
            res = self.env['year.year'].find(fiscal_date, True)
            if not res:
                raise UserError(_('Please define public year!'))
            return res[0] if res else False

    def calculate_leave_details(self):
        context = dict(self.env.context)
        context.update({'employee_id': self.employee_id.id})
        if self.request_date_from:
            fiscal_date = self.request_date_from
        else:
            fiscal_date = fields.Date.today()
        fiscalyear = self.get_fiscal_year(fiscal_date)
        self.leave_details.unlink()
        period_obj = self.env['year.period']
        contract_ids = self.employee_id._get_contracts(fiscalyear.date_start, fiscalyear.date_stop, states=['open'])
        # contract_ids = self.env['hr.contract'].browse(contract_ids).filtered(lambda contract: contract.resource_calendar_id)
        current_year_leaves_taken = 0
        if fiscalyear:
            requests = self.env['hr.leave'].search([
                ('employee_id', '=', self.employee_id.id),
                ('state', 'in', ['confirm', 'validate1', 'validate']),
                ('holiday_status_id', '=', self.holiday_status_id.id),
                ('request_date_from', '>=', fiscalyear.date_start),
                ('request_date_from', '<=', fiscalyear.date_stop),
                ('request_date_to', '<=', fiscalyear.date_stop),
            ])
            for request in requests:
                if request.state == 'validate':
                    current_year_leaves_taken += (request.number_of_hours_display
                                                if request.leave_type_request_unit == 'hour'
                                                else request.number_of_days)
        contract_ids = contract_ids.filtered(lambda contract: contract.resource_calendar_id)
        if contract_ids and contract_ids[0] and fiscalyear:
            resource_calendar_id = contract_ids and contract_ids[0].resource_calendar_id or self.employee_id.resource_calendar_id
            if resource_calendar_id:
                day_from = datetime.combine(fields.Date.from_string(self.date_from), time.min)
                day_to = datetime.combine(fields.Date.from_string(self.date_to), time.max)
                leave_day_from = self.date_from
                leave_day_to = self.date_to
                nb_of_days = (day_to - day_from).days + 1
                period_dict = {}
                for day in range(0, nb_of_days):
                    leave_date = (day_from + timedelta(days=day))
                    leave_day_counter = 1.0
                    period_id = period_obj.find(dt=leave_date.date(), fiscalyear_id=fiscalyear.id, exception=True)
                    if period_id:
                        if self.holiday_status_id.skip:
                            is_working_day = self.isWorkingDay(leave_date, employee_id=self.employee_id.id, contract_ids=contract_ids[0])
                            is_public_day = self.isPublicDay(leave_date, employee_id=self.employee_id.id, fiscalyear=fiscalyear)
                            if is_public_day:
                                continue
                            if not is_working_day:
                                continue
                        total_working_hours = 0.0
                        working_hours = contract_ids and contract_ids[0].resource_calendar_id.default_get('attendance_ids')['attendance_ids']
                        for hours in working_hours:
                            if int(hours[2].get('dayofweek')) == int(leave_day_from.weekday()):
                                diff = int(hours[2].get('hour_to')) - int(hours[2].get('hour_from'))
                                total_working_hours += diff
                        if not self.holiday_status_id.skip and total_working_hours == 0.0:
                            total_working_hours = resource_calendar_id.hours_per_day
                        if self.request_unit_half:
                            leave_day_counter = 0.5
                            total_working_hours = total_working_hours / 2
                        elif self.request_unit_hours:
                            # leave_start_stop_time = self.employee_id.get_start_stop_work_hour(self.date_from, self.date_to, resource_calendar_id)
                            # if leave_start_stop_time and leave_day_from and leave_date and leave_day_from.date() == leave_date.date() and leave_day_from > leave_start_stop_time[0]:
                            #     leave_day_counter = 0.5
                            #     total_working_hours = total_working_hours / 2
                            # if leave_start_stop_time and leave_day_to and leave_date and leave_day_to.date() == leave_date.date() and leave_day_to < leave_start_stop_time[1]:
                            #     leave_day_counter = 0.5
                            #     total_working_hours = total_working_hours / 2
                            leave_day_counter = self.number_of_days_display
                            total_working_hours = self.number_of_hours_display
                        if period_id.id in period_dict:
                            period_dict.update({period_id.id: [period_dict.get(period_id.id)[0] + leave_day_counter, period_dict.get(period_id.id)[1] + total_working_hours]})
                        else:
                            period_dict.update({period_id.id: [leave_day_counter, total_working_hours]})
                already_taken_dict = {}
                total_taken_leave = 0.0
                if period_dict and len(period_dict) > 1:
                    copy_period_dict = period_dict
                    first_key = list(copy_period_dict)[0]
                    for period_id, leave_day in copy_period_dict.items():
                        if period_id != first_key:
                            already_taken_dict.update({period_id: total_taken_leave})
                        if self.holiday_status_id.deduction_by == 'hour':
                            total_taken_leave += leave_day[1]
                        else:
                            total_taken_leave += leave_day[0]
                for period_id, leave_day in period_dict.items():
                    period_id = period_obj.browse(period_id)
                    leave_days = []
                    day_from = period_id.date_start
                    day_to = period_id.date_stop
                    day_from_datetime = datetime.combine(fields.Date.from_string(day_from), time.min)
                    day_to_datetime = datetime.combine(fields.Date.from_string(day_to), time.max)
                    nb_of_days = (day_to - day_from).days + 1
                    for day in range(0, nb_of_days):
                        day_from_start = datetime.strptime(((day_from + timedelta(days=day)).strftime("%Y-%m-%d 00:00:00")), DEFAULT_SERVER_DATETIME_FORMAT)
                        day_from_end = datetime.strptime(((day_from + timedelta(days=day)).strftime("%Y-%m-%d 23:59:59")), DEFAULT_SERVER_DATETIME_FORMAT)
                        if not day_from_start.tzinfo:
                            day_from_start = day_from_start.replace(tzinfo=utc)
                        if not day_from_end.tzinfo:
                            day_from_end = day_from_end.replace(tzinfo=utc)
                        day_from_start = day_from_start.astimezone(timezone(self.env.user.tz or 'UTC'))
                        day_from_end = day_from_end.astimezone(timezone(self.env.user.tz or 'UTC'))
                        day_intervals = resource_calendar_id._leave_intervals(resource=self.employee_id.resource_id, start_dt=day_from_start, end_dt=day_from_end)
                        for interval in day_intervals:
                            holiday = interval[2].holiday_id
                            if holiday.holiday_status_id.id == self.holiday_status_id.id:
                                if holiday.holiday_status_id.skip:
                                    continue
                                leave_time = (interval[1] - interval[0]).seconds / 3600
                                leave_days.append(1.0 if leave_time > 4.0 else 0.5)
                    day_leave_intervals = self.employee_id.list_leaves(day_from_datetime, day_to_datetime, calendar=resource_calendar_id)
                    tz = timezone(resource_calendar_id.tz)
                    for day, hours, leave in day_leave_intervals:
                        holiday = leave.holiday_id
                        if holiday.holiday_status_id.id == self.holiday_status_id.id and holiday.holiday_status_id.skip:
                            leave_time = hours
                            work_hours = resource_calendar_id.get_work_hours_count(
                                tz.localize(datetime.combine(day, time.min)),
                                tz.localize(datetime.combine(day, time.max)),
                                compute_leaves=False,
                            )
                            if work_hours:
                                leave_days.append(hours / work_hours)
                    paid_leaves = leave_day[0]
                    leave_hours = leave_day[1]
                    unpaid_leave_hours = leave_day[1]
                    total_leave_hours = leave_day[1]
                    unpaid_leave = 0.0

                    # already_taken = 0.0
                    # requests = self.env['hr.leave'].search([('employee_id', '=', self.employee_id.id),
                    #             ('state', 'in', ['confirm', 'validate1', 'validate']),
                    #             ('holiday_status_id', '=', self.holiday_status_id.id),
                    #             ('id', '!=', self.id)
                    #             ])
                    # for request in requests:
                    #     already_taken += ((request.number_of_hours_display / resource_calendar_id.hours_per_day)
                    #                         if request.leave_type_request_unit == 'hour'
                    #                         else request.number_of_days)

                    # already_taken = 0.0
                    # already_taken_hours = 0.0
                    # requests = self.env['hr.leave'].search([('employee_id', '=', self.employee_id.id),
                    #             ('state', 'in', ['confirm', 'validate1', 'validate']),
                    #             ('holiday_status_id', '=', self.holiday_status_id.id),
                    #             ('id', '!=', self.id)
                    #             ])
                    # for request in requests:
                    #     already_taken += ((request.number_of_hours_display / resource_calendar_id.hours_per_day)
                    #                         if request.leave_type_request_unit == 'hour'
                    #                         else request.number_of_days)
                    #     already_taken_hours += ((request.number_of_days * resource_calendar_id.hours_per_day)
                    #                             if request.leave_type_request_unit == 'day'
                    #                             else request.number_of_hours_display)

                    if self.holiday_status_id.is_deduction and self.holiday_status_id.deduction_by:
                        # total_leave_day = already_taken + leave_day[0]
                        # if self.holiday_status_id.deduction_by == 'day':
                        #     rule_line = self.holiday_status_id.rule_ids.filtered(lambda l: float(l.limit_from) <= float(total_leave_day) and float(l.limit_to) >= float(total_leave_day))
                        #     if rule_line:
                        #         days = 0
                        #         if rule_line[0].limit_from > 0:
                        #             days = (total_leave_day - (rule_line[0].limit_from - 1))
                        #         unpaid_leave = float(float((days * (100 - rule_line[0].limit_per)) / 100))
                        #         if self.holiday_status_id.work_entry_type_id.sudo().code == 'LEAVE90':
                        #             unpaid_leave = leave_day[0]
                        #         else:
                        #             paid_leaves = leave_day[0] - unpaid_leave
                        #         leave_hours = float(float(leave_hours * rule_line[0].limit_per) / 100)
                        # elif self.holiday_status_id.deduction_by == 'year':
                        #     year_start_date = date(date.today().year, 1, 1)
                        #     year_end_date = date(date.today().year, 12, 31) + timedelta(days=1)
                        #     year_days = year_end_date - year_start_date
                        #     year_days = float(total_leave_day / year_days.days)
                        #     rule_line = self.holiday_status_id.rule_ids.filtered(lambda l: float(l.limit_from) <= float(year_days) and float(l.limit_to) >= float(year_days))
                        #     if rule_line:
                        #         days = 0
                        #         if rule_line[0].limit_from > 0:
                        #             days = (total_leave_day - (rule_line[0].limit_from - 1))
                        #         unpaid_leave = float(float((days * (100 - rule_line[0].limit_per)) / 100))
                        #         paid_leaves = leave_day[0] - unpaid_leave
                        #         if self.holiday_status_id.work_entry_type_id.sudo().code == 'LEAVE130':
                        #             if self.employee_id and self.employee_id.date_of_join:
                        #                 diff = relativedelta(datetime.today(), datetime.strptime(str(self.employee_id.date_of_join), DEFAULT_SERVER_DATE_FORMAT))
                        #                 rule_ids = self.holiday_status_id.rule_ids.filtered(lambda l: float(l.limit_from) <= float(diff.years) and float(l.limit_to) >= float(diff.years))
                        #                 if rule_ids:
                        #                     unpaid_leave = float(float((leave_day[0] * (100 - rule_ids[0].limit_per)) / 100))
                        #                     paid_leaves = leave_day[0] - unpaid_leave
                        leaves_taken = self.holiday_status_id.with_context(context).leaves_taken
                        leaves_taken = current_year_leaves_taken
                        if len(period_dict) > 1 and period_id.id in already_taken_dict:
                            leaves_taken += already_taken_dict.get(period_id.id)
                        total_leave_day = leaves_taken + leave_day[0]
                        if self.holiday_status_id.deduction_by == 'hour':
                            total_leave_day = leaves_taken + leave_day[1]
                        else:
                            total_leave_day = leaves_taken + leave_day[0]

                        if self.holiday_status_id.deduction_by == 'day':
                            rule_line = self.holiday_status_id.rule_ids.filtered(lambda l: float(l.limit_from) <= float(total_leave_day) and float(l.limit_to) >= float(total_leave_day))
                            if total_leave_day > paid_leaves:
                                diff_days = float(total_leave_day - paid_leaves)
                                previous_rule_line = False
                                if rule_line and float(rule_line[0].limit_from) > diff_days:
                                    previous_rule_line = self.holiday_status_id.rule_ids.filtered(lambda l: float(l.limit_from) <= float(diff_days) and float(l.limit_to) >= float(diff_days))
                                if previous_rule_line and diff_days:
                                    leave_hours = 0.0
                                    paid_leaves = 0.0
                                    previous_diff_days = (previous_rule_line.limit_to - diff_days)
                                    paid_leaves = float(float(previous_diff_days * previous_rule_line[0].limit_per) / 100)
                                    new_diff_leave = leave_day[0] - previous_diff_days
                                    while previous_rule_line.next_line_id and previous_rule_line.next_line_id.id != rule_line.id:
                                        if previous_rule_line.next_line_id.id == rule_line.id:
                                            break
                                        previous_rule_line = previous_rule_line.next_line_id
                                        difference = (previous_rule_line.limit_to - previous_rule_line.limit_from) + 1
                                        paid_leaves += float(float(difference * previous_rule_line.limit_per) / 100)
                                        new_diff_leave -= difference
                                    if rule_line:
                                        paid_leaves += float(float(new_diff_leave * rule_line[0].limit_per) / 100)
                                        if leave_day[0] > 0.0:
                                            leave_hours = float((paid_leaves * leave_day[1]) / leave_day[0])
                                        else:
                                            leave_hours = float(float(leave_hours * rule_line[0].limit_per) / 100)
                                elif rule_line:
                                    paid_leaves = float(float(paid_leaves * rule_line[0].limit_per) / 100)
                                    leave_hours = float(float(leave_hours * rule_line[0].limit_per) / 100)
                            elif rule_line:
                                if current_year_leaves_taken == 0:
                                    new_paid_leaves = 0
                                    new_paid_hours = 0
                                    current_rule_line = rule_line
                                    while rule_line.previous_line_id and rule_line.previous_line_id.limit_to:
                                        increase_number = 0
                                        if rule_line.previous_line_id.limit_from != 0:
                                            increase_number = 1
                                        paid_days_diff = rule_line.previous_line_id.limit_to - rule_line.previous_line_id.limit_from + increase_number
                                        paid_hours_diff = paid_days_diff * resource_calendar_id.hours_per_day
                                        new_paid_leaves += float(float(paid_days_diff * rule_line.previous_line_id.limit_per) / 100)
                                        new_paid_hours += float(float(paid_hours_diff * rule_line.previous_line_id.limit_per) / 100)
                                        rule_line = rule_line.previous_line_id
                                    if current_rule_line.previous_line_id:
                                        paid_leaves -= new_paid_leaves
                                        leave_hours -= new_paid_hours
                                        current_paid_leave = float(float(paid_leaves * current_rule_line[0].limit_per) / 100)
                                        current_leave_hours = float(float(leave_hours * current_rule_line[0].limit_per) / 100)
                                        paid_leaves = current_paid_leave + new_paid_leaves
                                        leave_hours = current_leave_hours + new_paid_hours
                                    else:
                                        paid_leaves = float(float(paid_leaves * rule_line[0].limit_per) / 100)
                                        leave_hours = float(float(leave_hours * rule_line[0].limit_per) / 100)
                                else:
                                    paid_leaves = float(float(paid_leaves * rule_line[0].limit_per) / 100)
                                    leave_hours = float(float(leave_hours * rule_line[0].limit_per) / 100)

                        elif self.holiday_status_id.deduction_by == 'year':
                            year_start_date = date(date.today().year, 1, 1)
                            year_end_date = date(date.today().year, 12, 31) + timedelta(days=1)
                            year_days = year_end_date - year_start_date
                            year_days = round(float(total_leave_day / year_days.days), 2)
                            rule_line = self.holiday_status_id.rule_ids.filtered(lambda l: float(l.limit_from) <= float(year_days) and float(l.limit_to) >= float(year_days))
                            if rule_line:
                                paid_leaves = float(float(paid_leaves * rule_line[0].limit_per) / 100)
                                leave_hours = float(float(leave_hours * rule_line[0].limit_per) / 100)

                        elif self.holiday_status_id.deduction_by == 'hour':
                            rule_line = self.holiday_status_id.rule_ids.filtered(lambda l: float(l.limit_from) <= float(total_leave_day) and float(l.limit_to) >= float(total_leave_day))
                            if total_leave_day > leave_hours and rule_line:
                                rule_line = rule_line[0]
                                diff_hours = float(total_leave_day - leave_hours)
                                previous_rule_line = False
                                if rule_line and float(rule_line[0].limit_from) > diff_hours:
                                    previous_rule_line = self.holiday_status_id.rule_ids.filtered(lambda l: float(l.limit_from) <= float(diff_hours) and float(l.limit_to) >= float(diff_hours))
                                leave_hours = 0.0
                                paid_leaves = 0.0
                                if previous_rule_line and diff_hours:
                                    previous_rule_line = previous_rule_line[0]
                                    previous_diff_hours = (previous_rule_line.limit_to - diff_hours)
                                    leave_hours = float(float(previous_diff_hours * previous_rule_line.limit_per) / 100)

                                    new_diff_hours = leave_day[1] - previous_diff_hours
                                    while previous_rule_line.next_line_id and previous_rule_line.next_line_id.id != rule_line.id:
                                        if previous_rule_line.next_line_id.id == rule_line.id:
                                            break
                                        previous_rule_line = previous_rule_line.next_line_id
                                        difference = (previous_rule_line.limit_to - previous_rule_line.limit_from) + 1
                                        leave_hours += float(float(difference * previous_rule_line.limit_per) / 100)
                                        new_diff_hours -= difference
                                    if rule_line:
                                        leave_hours += float(float((new_diff_hours) * rule_line[0].limit_per) / 100)
                                        if leave_day[1] > 0.0:
                                            paid_leaves = float((leave_hours * leave_day[0]) / leave_day[1])
                                        else:
                                            paid_leaves = float(float(paid_leaves * rule_line[0].limit_per) / 100)
                                elif rule_line:
                                    paid_leaves = float(float(paid_leaves * rule_line[0].limit_per) / 100)
                                    leave_hours = float(float(leave_hours * rule_line[0].limit_per) / 100)
                            elif rule_line:
                                if current_year_leaves_taken == 0:
                                    new_paid_leaves = 0
                                    new_paid_hours = 0
                                    current_rule_line = rule_line
                                    while rule_line.previous_line_id and rule_line.previous_line_id.limit_to:
                                        increase_number = 0
                                        if rule_line.previous_line_id.limit_from != 0:
                                            increase_number = 1
                                        paid_hours_diff = rule_line.previous_line_id.limit_to - rule_line.previous_line_id.limit_from + increase_number
                                        paid_days_diff = (paid_hours_diff / resource_calendar_id.hours_per_day)
                                        new_paid_leaves += float(float(paid_days_diff * rule_line.previous_line_id.limit_per) / 100)
                                        new_paid_hours += float(float(paid_hours_diff * rule_line.previous_line_id.limit_per) / 100)
                                        rule_line = rule_line.previous_line_id
                                    if current_rule_line.previous_line_id:
                                        paid_leaves -= new_paid_leaves
                                        leave_hours -= new_paid_hours
                                        current_paid_leave = float(float(paid_leaves * current_rule_line[0].limit_per) / 100)
                                        current_leave_hours = float(float(leave_hours * current_rule_line[0].limit_per) / 100)
                                        paid_leaves = current_paid_leave + new_paid_leaves
                                        leave_hours = current_leave_hours + new_paid_hours
                                    else:
                                        paid_leaves = float(float(paid_leaves * rule_line[0].limit_per) / 100)
                                        leave_hours = float(float(leave_hours * rule_line[0].limit_per) / 100)
                                else:
                                    paid_leaves = float(float(paid_leaves * rule_line[0].limit_per) / 100)
                                    leave_hours = float(float(leave_hours * rule_line[0].limit_per) / 100)
                    # unpaid_leave_hours = unpaid_leave * resource_calendar_id.hours_per_day
                    # leave_hours = paid_leaves * resource_calendar_id.hours_per_day
                    unpaid_leave_hours = leave_day[1] - leave_hours
                    unpaid_leave = (leave_day[0] - paid_leaves)
                    #             days = 0
                    #             if rule_line[0].limit_from > 0:
                    #                 days = (total_leave_day - (rule_line[0].limit_from - 1))
                    #             unpaid_leave = float(float((days * (100 - rule_line[0].limit_per)) / 100))
                    #             paid_leaves = leave_day[0] - unpaid_leave
                    #             if self.holiday_status_id.work_entry_type_id.sudo().code == 'LEAVE130':
                    #                 if self.employee_id and self.employee_id.date_of_join:
                    #                     diff = relativedelta(datetime.today(), datetime.strptime(str(self.employee_id.date_of_join), DEFAULT_SERVER_DATE_FORMAT))
                    #                     rule_ids = self.holiday_status_id.rule_ids.filtered(lambda l: float(l.limit_from) <= float(diff.years) and float(l.limit_to) >= float(diff.years))
                    #                     if rule_ids:
                    #                         unpaid_leave = float(float((leave_day[0] * (100 - rule_ids[0].limit_per)) / 100))
                    #                         paid_leaves = leave_day[0] - unpaid_leave
                    #     elif self.holiday_status_id.deduction_by == 'hour':
                    #         total_leave_hours = already_taken_hours + leave_day[1]
                    #         rule_line = self.holiday_status_id.rule_ids.filtered(lambda l: float(l.limit_from) <= float(total_leave_hours) and float(l.limit_to) >= float(total_leave_hours))
                    #         if rule_line:
                    #             hours = 0
                    #             if rule_line[0].limit_from > 0:
                    #                 hours = (total_leave_hours - (rule_line[0].limit_from - 1))
                    #             unpaid_leave = float(float((hours * (100 - rule_line[0].limit_per)) / 100))
                    #             if self.holiday_status_id.work_entry_type_id.sudo().code == 'LEAVE90':
                    #                 unpaid_leave = leave_day[1]
                    #             else:
                    #                 paid_leaves = leave_day[1] - unpaid_leave
                    #             leave_hours = float(float(leave_hours * rule_line[0].limit_per) / 100)
                    # unpaid_leave_hours = unpaid_leave * resource_calendar_id.hours_per_day
                    # leave_hours = paid_leaves * resource_calendar_id.hours_per_day
                    leave_detail_id = self.env['leave.detail'].create({
                            'leave_id': self.id,
                            'name': period_id.name,
                            'already_taken_month': sum(leave_days),
                            # 'already_taken': already_taken,
                            'already_taken': self.holiday_status_id.with_context(context).leaves_taken,
                            'paid_leave': paid_leaves,
                            'unpaid_leave': unpaid_leave,
                            'total_leave': leave_day[0],
                            'leave_hours': leave_hours,
                            'unpaid_leave_hours': unpaid_leave_hours,
                            'total_leave_hours': total_leave_hours,
                            'period_id': period_id.id
                        })


    def leave_mail(self):
        try:
            template_id = self.env.ref('saudi_hr_leaves_management.email_template_for_leave_used')
        except ValueError:
            template_id = False
        if self.employee_id and self.employee_id.remaining_leaves <= 0 and template_id:
            hr_id = self.employee_id.hr_id or False
            if not hr_id:
                hr = self.env['ir.config_parameter'].sudo().get_param('saudi_hr.hr_id')
                hr_id = self.env['hr.employee'].browse(int(hr))
            if hr_id:
                template_id.with_context(hr_id=hr_id).send_mail(self.id, force_send=True)

    def send_by_email(self):
        ctx = {
            'default_model': 'hr.leave',
            'default_res_id': self.id,
            'default_use_template': False,
            # 'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'force_email': True,
            # 'default_attachment_ids': [(6, 0, attachment_list)]
        }

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'context': ctx,
            'target': 'new',
        }

    @api.model
    def create(self, values):
        res = super(HolidaysRequest, self).create(values)
        if res.date_from or res.date_to or res.holiday_status_id or res.employee_id or res.number_of_days:
            res.calculate_leave_details()
        res.leave_mail()
        return res

    def write(self, values):
        res = super(HolidaysRequest, self).write(values)
        for obj in self:
            if (values.get('date_from') or values.get('date_to')
                    or values.get('holiday_status_id') or values.get('employee_id')
                    or values.get('number_of_days')):
                obj.calculate_leave_details()
            obj.leave_mail()
        return res

    # def action_validate(self):
    #     res = super(HolidaysRequest, self).action_validate()
    #     for rec in self:
    #         rec.calculate_leave_details()
    #     return res

    # def _check_approval_update(self, state):
    #     """ Check if target state is achievable. """
    #     current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
    #     is_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
    #     is_manager = self.env.user.has_group('hr_holidays.group_hr_holidays_manager')
    #     is_line_manager = self.env.user.has_group('saudi_hr.group_line_manager')
    #     is_hod = self.env.user.has_group('saudi_hr.group_hof')
    #     for holiday in self:
    #         val_type = holiday.holiday_status_id.validation_type
    #         if state == 'confirm':
    #             continue

    #         if state == 'draft':
    #             if holiday.employee_id != current_employee and not is_manager:
    #                 raise UserError(_('Only a Leave Manager can reset other people leaves.'))
    #             continue

    #         if is_officer:
            #     # use ir.rule based first access check: department, members, ... (see security.xml)
            #     holiday.check_access_rule('write')
            # else:
            #     if not is_line_manager and not is_hod:
            #         raise UserError(_('Only a Leave Officer or Manager can approve or refuse leave requests.'))
            #     if is_hod:
            #         hod_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
            #         hod_approval = holiday.employee_id.coach_id.user_id.id == self.env.uid or \
            #                    holiday.department_id.manager_id.user_id.id == self.env.uid or \
            #                    hod_id.department_id.child_ids in holiday.employee_id.department_id
            #         if not hod_approval:
            #             raise UserError(_('You have no rights to approve this leave please contact you administrator.'))
            #     elif is_line_manager:
            #         line_manager_approval = holiday.employee_id.parent_id.user_id.id == self.env.uid
            #         if not line_manager_approval:
            #             raise UserError(_('You have no rights to approve this leave please contact you administrator.'))

            # if holiday.employee_id == current_employee and not is_manager:
            #     raise UserError(_('Only a Leave Manager can approve its own requests.'))

            # if (state == 'validate1' and val_type == 'both') or (state == 'validate' and val_type == 'manager'):
            #     manager = holiday.employee_id.parent_id or holiday.employee_id.department_id.manager_id
            #     if (manager and manager != current_employee) and not self.env.user.has_group(
            #             'hr_holidays.group_hr_holidays_manager'):
            #         raise UserError(_('You must be either %s\'s manager or Leave manager to approve this leave') % (
            #             holiday.employee_id.name))

            # if state == 'validate' and val_type == 'both':
            #     if not self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
            #         raise UserError(_('Only an Leave Manager can apply the second approval on leave requests.'))
