# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models


class Project(models.Model):
    _inherit = "project.project"

    department_id = fields.Many2one("hr.department", string="Department")
