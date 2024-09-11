# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import date, datetime, time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _get_worked_day_lines(self):
        res = super (HrPayslip, self)._get_worked_day_lines()
        attendance_work_entry = self.env.ref('hr_work_entry.work_entry_type_attendance')
        fiscalyear = self.env['year.year'].find(fields.Date.today(), True)
        contract = self.contract_id
        date_from = datetime.combine(self.date_from, datetime.min.time())
        date_to = datetime.combine(self.date_to, datetime.max.time())
        if contract.resource_calendar_id:
            work_entries = self.env['hr.work.entry'].search(
            [
                ('state', 'in', ['validated', 'draft']),
                ('date_start', '>=', date_from),
                ('date_stop', '<=', date_to),
                ('contract_id', '=', contract.id),
                ('overtime_hours', '>', '0.0'),
                ('work_entry_type_id', '=', attendance_work_entry.id)
            ])
            working_days_hours = 0
            public_holidays_hours = 0
            weekends_hours = 0
            work_entries_dict = {}
            for rec in work_entries:
                is_working_day = self.env['hr.leave'].isWorkingDay(rec.date_start.date(), employee_id=self.employee_id.id, contract_ids=contract)
                is_public_day = self.env['hr.leave'].isPublicDay(rec.date_start.date(), employee_id=self.employee_id.id, fiscalyear=fiscalyear)
                is_weekend = self.env['hr.leave'].isweekend(rec.date_start.date(), contract=contract)
                if is_public_day:
                    public_holidays_hours += rec.overtime_hours
                elif is_weekend:
                    weekends_hours += rec.overtime_hours
                elif is_working_day:
                    # work_entry = self.env['hr.work.entry'].search([('date_start', '=', rec.date_start.date())])
                    work_entry = self.env['hr.work.entry'].search([('date_start', '>=', datetime.strptime(rec.date_start.strftime('%Y-%m-%d 00:00:00'),  DEFAULT_SERVER_DATETIME_FORMAT)),
                                                                   ('date_stop', '<=', datetime.strptime(rec.date_stop.strftime('%Y-%m-%d 23:59:59'),  DEFAULT_SERVER_DATETIME_FORMAT)),
                                                                   ('state', 'in', ['validated', 'draft']),
                                                                   ('contract_id', '=', contract.id),
                                                                   ('work_entry_type_id', '=', attendance_work_entry.id)
                                                                   ])
                    for line in work_entry:
                        if line.id not in work_entries.ids:
                            work_entries_dict[line.date_start.date()] = {'working_hours': line.duration,
                                                                        'overtime_hours': line.overtime_hours}
                        # else:
                        #     work_entries_dict[rec.date_start.date()]['working_hours'] += rec.duration
                        #     work_entries_dict[rec.date_start.date()]['overtime_hours'] += rec.overtime_hours
                    if rec.date_start.date() in work_entries_dict:
                        work_entries_dict[rec.date_start.date()]['working_hours'] += rec.duration
                        work_entries_dict[rec.date_start.date()]['overtime_hours'] += rec.overtime_hours
                    else:
                        work_entries_dict[rec.date_start.date()] = {'working_hours': rec.duration, 'overtime_hours': rec.overtime_hours}

                    if work_entries_dict[rec.date_start.date()]['working_hours'] >= contract.resource_calendar_id.hours_per_day:
                        if contract.overtime_limit and work_entries_dict[rec.date_start.date()]['overtime_hours'] > contract.overtime_limit:
                            working_days_hours = contract.overtime_limit
                        elif contract.overtime_limit and work_entries_dict[rec.date_start.date()]['overtime_hours'] < contract.overtime_limit:
                            working_days_hours += work_entries_dict[rec.date_start.date()]['overtime_hours']
                        else:
                            working_days_hours += work_entries_dict[rec.date_start.date()]['overtime_hours']
            if working_days_hours > 0:
                res.append({'work_entry_type_id':  self.env.ref('sync_hr_overtime.work_entry_type_normal_working_days_overtime').id,
                    'name': 'Working days Overtime',
                    'number_of_days': working_days_hours / contract.resource_calendar_id.hours_per_day,
                    'number_of_hours': working_days_hours,
                    'amount': 0.0,
                    })
            if public_holidays_hours > 0:
                res.append({'work_entry_type_id':  self.env.ref('sync_hr_overtime.work_entry_type_public_holiday_overtime').id,
                    'name': 'Public Holidays Overtime',
                    'number_of_days': public_holidays_hours / contract.resource_calendar_id.hours_per_day,
                    'number_of_hours': public_holidays_hours,
                    'amount': 0.0,
                    })
            if weekends_hours > 0:
                res.append({'work_entry_type_id':  self.env.ref('sync_hr_overtime.work_entry_type_weekend_overtime').id,
                    'name': 'Weekend days Overtime',
                    'number_of_days': weekends_hours / contract.resource_calendar_id.hours_per_day,
                    'number_of_hours': weekends_hours,
                    'amount': 0.0,
                    })
        return res