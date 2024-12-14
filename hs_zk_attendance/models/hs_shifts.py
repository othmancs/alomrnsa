from odoo import models, api, fields


class HsShifts(models.Model):
    _name = 'hs.shifts'
    _description = "Timing Shifts"

    name = fields.Char(string="Shift Name")
    shift_in = fields.Float(string="Shift Time-In" ,help="Timing Standard Must be 24 hours format")
    shift_out = fields.Float(string="Shift Time-Out", help="Timing Standard Must be 24 hours format")
    active = fields.Boolean(string="Status", default=True)
