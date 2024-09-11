# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class Employee(models.Model):
    _inherit = "hr.employee"

    branch_id = fields.Many2one('hr.branch', 'Branch', tracking=True)

