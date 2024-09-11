# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models


class HrPunishment(models.Model):
    _name = "hr.punishment"
    _description = "Hr Punishment"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Punishment", required=True, tracking=True)
    p_type = fields.Selection(
        [
            ("warning", "Warning"),
            ("penalty", "Penalty"),
            ("termination", "Termination"),
        ],
        default="warning",
        required=True,
        string="Type",
        tracking=True,
    )
    punishment_type = fields.Selection(
        [("fixed_amount", "Fixed Amount"), ("depend_on_salary", "Depends on Salary")],
        default="fixed_amount",
        string="Punishment Type",
        tracking=True,
    )
    penalty_amt = fields.Float(string="Fixed Amount", default=0.0, tracking=True)
    punishment_type_amount = fields.Selection(
        [("duration", "Duration"), ("percentage", "Percentage")],
        default="duration",
        string="Amount of Penalty Type",
        tracking=True,
    )
    penalty_duration = fields.Float(
        string="Duration (In Days)", default=0.0, tracking=True
    )
    penalty_percentage = fields.Float(string="Percentage", default=0.0, tracking=True)
