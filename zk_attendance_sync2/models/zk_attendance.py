from odoo import models, fields

class ZKAttendance(models.Model):
    _name = 'zk.attendance'
    _description = 'ZK Attendance'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    check_in = fields.Datetime(string='Check In')
    check_out = fields.Datetime(string='Check Out')
