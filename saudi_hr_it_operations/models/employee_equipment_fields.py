# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class EmpEquipmentFields(models.Model):
    _name = 'employee.equipment.fields'
    _description = 'Employee Equipment Fields'

    employee_registration_id = fields.Many2one('hr.employee.registration', string='Employee Asset Registrations')
    equipment_registration_id = fields.Many2one('equipment.registration', string='Equipment')
    question_name = fields.Char(string='Question')
    answer = fields.Char(string='Answer')
