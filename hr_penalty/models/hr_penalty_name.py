# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models


class HrPenaltyName(models.Model):
    _name = "hr.penalty.name"
    _description = "Hr Penalty Name"

    name = fields.Char(string="Penalty Type", copy=False)
