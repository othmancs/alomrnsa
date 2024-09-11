# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _


class HrJob(models.Model):
    _inherit = 'hr.job'

    min_salary = fields.Integer('Minimum Salary')
    max_salary = fields.Integer('Maximum Salary')
