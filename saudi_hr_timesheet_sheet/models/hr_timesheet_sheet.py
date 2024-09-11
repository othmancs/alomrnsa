# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models


class hr_timesheet_sheet_sheet_day(models.Model):
    _name = "hr_timesheet_sheet_sheet_day"
    _description = "Timesheets by Period"
    _order = "name"

    name = fields.Date("Date", readonly=True)
    total_timesheet = fields.Float(string="Total Timesheet", readonly=True)
    total_attendance = fields.Float(string="Attendance", readonly=True)
    total_difference = fields.Float(string="Difference", readonly=True)
    total_overtime = fields.Float(string="Overtime", readonly=True)
    total_working_hours = fields.Float(string="Working Hours", readonly=True)
    reason = fields.Char(string="Reason", readonly=True)
    holiday_ids = fields.Many2many("hr.leave", string="Leave Request")
