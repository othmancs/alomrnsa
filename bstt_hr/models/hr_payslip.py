# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    employee_no = fields.Char(related="employee_id.employee_no", store="True")
