
from odoo import models, fields, api, _
from pytz import utc


class ResourceMixin(models.AbstractModel):
    _inherit = "resource.mixin"

    def get_start_stop_work_hour(self, start_dt, end_dt, calendar=None):
        calendar = calendar or self.resource_calendar_id
        if not start_dt.tzinfo:
            start_dt = start_dt.replace(tzinfo=utc)
        if not end_dt.tzinfo:
            end_dt = end_dt.replace(tzinfo=utc)
        work_intervals = calendar._work_intervals(start_dt, end_dt, resource=self.resource_id)
        for start, stop, meta in work_intervals:
            return start.replace(tzinfo=None), stop.replace(tzinfo=None)
        return False


class ResourceCalendarLeaves(models.Model):
    _inherit = "resource.calendar.leaves"

    public_line_id = fields.Many2one('hr.holidays.public.line', string='Public Holiday')
