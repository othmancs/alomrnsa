# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models


class HrPenalty(models.Model):
    _name = "hr.penalty"
    _description = "Hr Penalty"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Penalty", required=True, tracking=True)
    penalty_type_id = fields.Many2one(
        "hr.penalty.name", required=True, string="Penalty Type", tracking=True
    )
    penalty_code = fields.Char(string="Code", copy=False)
    have_punishment = fields.Boolean("Have Punishment ?")
    first_time = fields.Many2many(
        "hr.punishment",
        "penalty_punishment_rel_first",
        "penalty_id",
        "punishment_id",
        string="First Time",
    )
    second_time = fields.Many2many(
        "hr.punishment",
        "penalty_punishment_rel_second",
        "penalty_id",
        "punishment_id",
        string="Second Time",
    )
    third_time = fields.Many2many(
        "hr.punishment",
        "penalty_punishment_rel_third",
        "penalty_id",
        "punishment_id",
        string="Third Time",
    )
    fourth_time = fields.Many2many(
        "hr.punishment",
        "penalty_punishment_rel_fourth",
        "penalty_id",
        "punishment_id",
        string="Fourth Time",
    )
    fifth_time = fields.Many2many(
        "hr.punishment",
        "penalty_punishment_rel_fifth",
        "penalty_id",
        "punishment_id",
        string="Fifth Time",
    )

    @api.model_create_multi
    def create(self, values):
        """
        Override method for the creating sequence
        """
        for val in values:
            val["penalty_code"] = self.env["ir.sequence"].next_by_code("hr.penalty")
        return super(HrPenalty, self).create(values)
