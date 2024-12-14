# -*- coding: utf-8 -*-

from odoo import fields, models


class HrEmployee(models.Model):
    """Inherit the model to add field"""
    _inherit = 'hr.employee'

    device_id_num = fields.Char(string='Biometric Device ID',
                                help="Give the biometric device id")
    shift_id = fields.Many2one('hs.shifts',string="Time Shift")
