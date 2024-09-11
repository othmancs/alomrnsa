# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields


class HRDepartment(models.Model):
    _inherit = 'hr.department'

    probation_duration = fields.Integer(string='Probation Months', default=3, help='Probation Duration in Months for New Employees')
