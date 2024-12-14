# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ZkMachineAttendance(models.Model):
    """Model to hold data from the biometric device"""
    _name = 'zk.machine.attendance'
    _description = 'Attendance'
    _inherit = 'hr.attendance'

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """Overriding the __check_validity function for employee attendance."""
        pass

    device_id_num = fields.Char(string='Biometric Device ID',
                                help="The ID of the Biometric Device")
    check_in = fields.Datetime(string='Check In')
    check_out = fields.Datetime(string='Check Out')
    punching_time = fields.Datetime(string='Punching Time',
                                    help="Punching time in the device")
    i_check = fields.Char(string="Check Type")
    o_check = fields.Char(string="Check Type")
    is_danger = fields.Boolean(default=True)