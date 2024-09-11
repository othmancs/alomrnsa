# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Employee(models.Model):
    _inherit = "hr.employee"

    emp_health_ids = fields.One2many('emp.health.info', 'employee_id', string="Health Information")
