# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    iqama_ids = fields.One2many('hr.employee.iqama', 'employee_id')
    iqama_number = fields.Char(string="Iqama No.", compute='_compute_iqama_number')

    def _compute_iqama_number(self):
        for employee in self:
            iqama = ""
            for iq in employee.iqama_ids:
                if iq.relation == "self":
                    iqama = iq.iqama_number
            employee.iqama_number = iqama


