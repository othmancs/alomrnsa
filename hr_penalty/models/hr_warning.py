# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models


class IssueWarning(models.Model):
    _inherit = "issue.warning"

    pen_reg_id = fields.Many2one("hr.penalty.register", string="Penalty")
