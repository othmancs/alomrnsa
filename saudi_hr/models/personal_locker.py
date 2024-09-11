# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class EWSEmployeeLockerTracker(models.Model):
    _name = 'ews.employee.locker.tracker'
    _description = 'EWS Employee Locker Tracker'

    number = fields.Char(string='Locker Number')
    employee_code = fields.Char(string='Employee #', related='employee_id.code')
    employee_id = fields.Many2one('hr.employee', string='Employee Name')
    locker_combination = fields.Char(string='Combination')
    locker_serial_number = fields.Char(string='Serial Number')


class EWSEmployeePersonalVehicle(models.Model):
    _name = 'ews.employee.personal.vehicle'
    _description = 'EWS Employee Personal Vehicle'

    employee_id = fields.Many2one('hr.employee', string='Employee')
    ee_number = fields.Char(string='Make/Mode/Color')
    plant_name = fields.Char(string='Plant')
    department_id = fields.Many2one('hr.department', related="employee_id.department_id", string='Department')
    vehicle_number_plate = fields.Char(string='Plate')

    def name_get(self):
        res = []
        for record in self:
            name = record.employee_id.display_name
            if record.ee_number:
                name += ' [' + record.ee_number + ']'
            res.append((record.id, name))
        return res
