# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date, datetime
from odoo import api, models, fields, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import pytz


class EmployeeReportAttendance(models.AbstractModel):
    _name = 'report.sync_employee_attendance_report.attendance_report_view'
    _description = 'Employee Attendance Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start_obj = datetime.combine(datetime.strptime(data['form']['date_start'], DATE_FORMAT), datetime.min.time())
        date_end_obj = datetime.combine(datetime.strptime(data['form']['date_end'], DATE_FORMAT), datetime.max.time())
        docs = []
        attendance_info = {}
        timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
        print("== data['form']['employee_ids']===",  data['form']['employee_ids'])
        for employee in data['form']['employee_ids']:
            print("==employee---", employee)
            total_hours = []
            attendance_ids = self.env['hr.attendance'].search([('employee_id', '=', employee),
                                                                ('check_in', '>=', date_start_obj),
                                                                ('check_out', '<=', date_end_obj),
                                                                ('worked_hours', '<', 24)])
            print("=====attendance_ids==", attendance_ids)
            for attendance in attendance_ids:
                delta = attendance.check_out.astimezone(timezone) - attendance.check_in.astimezone(timezone)
                result = 0
                (h, m, s) = str(delta).split(':')
                result = int(h) * 3600 + int(m) * 60 + int(s)
                total_hours.append(result)
                docs.append({
                    'employee': attendance.employee_id.name,
                    'check_in': datetime.strftime(attendance.check_in.astimezone(timezone), DEFAULT_SERVER_DATETIME_FORMAT),
                    'check_out': datetime.strftime(attendance.check_out.astimezone(timezone), DEFAULT_SERVER_DATETIME_FORMAT),
                    'delta': delta,
                    })
                total = sum(total_hours)
                hours, remainder = divmod(total, 3600)
                minutes, seconds = divmod(remainder, 60)
                total_time_hours = ''
                total_time_hours = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
                attendance_info[employee] = {
                    'emp_name': attendance.employee_id.name,
                    'department': attendance.department_id.name,
                    'docs': docs,
                    'time1': total_time_hours,
                    }
        if not attendance_info:
            raise UserError(_('No records Found !'))
        return {
            'doc_ids': attendance,
            'doc_model': 'hr_attendance.hr.attendance',
            'attendance_info': attendance_info,
            }
