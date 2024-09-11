# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HRWorkLocation(models.Model):
    _inherit = "hr.work.location"

    green_belt_count = fields.Integer(
        string="No. Green Belt", compute="compute_green_belt_count"
    )
    blue_belt_count = fields.Integer(
        string="No. Blue Belt", compute="compute_blue_belt_count"
    )
    black_belt_count = fields.Integer(
        string="No. Black Belt", compute="compute_black_belt_count"
    )

    def compute_green_belt_count(self):
        for rec in self:
            rec.green_belt_count = rec.env["hr.employee"].search_count(
                [
                    ("work_location_id", "=", rec.id),
                    ("belt_level_id.name", "=", "Green"),
                ]
            )

    def compute_blue_belt_count(self):
        for rec in self:
            rec.blue_belt_count = rec.env["hr.employee"].search_count(
                [
                    ("work_location_id", "=", rec.id),
                    ("belt_level_id.name", "=", "Blue"),
                ]
            )

    def compute_black_belt_count(self):
        for rec in self:
            rec.black_belt_count = rec.env["hr.employee"].search_count(
                [
                    ("work_location_id", "=", rec.id),
                    ("belt_level_id.name", "=", "Black"),
                ]
            )


class BeltLevel(models.Model):
    _name = "belt.level"
    _description = "Belt Level"

    name = fields.Char(string="Belt Level")
    min_range = fields.Float(string="Min")
    max_range = fields.Float(string="Max")

    @api.constrains("min_range", "max_range")
    def check_range(self):
        for rec in self:
            if rec.min_range >= rec.max_range:
                raise ValidationError(
                    _(
                        "Error!\nThe start date of a calendar year must precede its end date."
                    )
                )
            available_range = self.search_count(
                [
                    ("min_range", "<=", rec.max_range),
                    ("max_range", ">=", rec.min_range),
                    ("id", "!=", self.id),
                ]
            )
            if available_range:
                raise ValidationError(_("You can not have range that overlaps!"))


class HREmployee(models.Model):
    _inherit = "hr.employee"

    belt_id = fields.Many2one(
        "belt.level",
        string="Belt Level",
        compute="set_belt_level",
        compute_sudo=True
    )
    belt_level_id = fields.Many2one(
        "belt.level",
        string="Belt Level",
        compute="set_belt_level",
        compute_sudo=True,
        store="True",
    )

    def set_belt_level(self):
        for rec in self:
            rec.belt_id = False
            contract = rec.get_current_contracts()
            if contract and contract.wage:
                wage_per_hour = (contract.wage / 30) / 8
                belt_id = self.env["belt.level"].search(
                    [
                        ("min_range", "<=", wage_per_hour),
                        ("max_range", ">=", wage_per_hour),
                    ],
                    limit=1,
                )
                rec.belt_id = belt_id and belt_id.id or False
                rec.belt_level_id = belt_id and belt_id.id or False


class EmployeeProbationReview(models.Model):
    _inherit = "emp.probation.review"

    wage_per_hour = fields.Float(string="Wage (per hour)")

    @api.constrains("wage_per_hour")
    def _check_wage_per_hour(self):
        for rec in self:
            if rec.wage_per_hour < 0:
                raise ValidationError(_("Wage (per hour) must be positive!"))


class ContractType(models.Model):
    _inherit = "hr.contract.type"

    is_probation = fields.Boolean(string="Is Probation")
    is_employeement = fields.Boolean(string="Is Employeement")

    @api.onchange("is_probation")
    def onchange_is_probation(self):
        if self.is_probation and self.is_employeement:
            self.is_employeement = False

    @api.onchange("is_employeement")
    def onchange_is_employeement(self):
        if self.is_probation and self.is_employeement:
            self.is_probation = False


class Contract(models.Model):
    _inherit = "hr.contract"

    probation_id = fields.Many2one("emp.probation.review", string="Probation")
    is_probation = fields.Boolean(
        related="contract_type_id.is_probation", string="Is probation"
    )

    @api.onchange("probation_id")
    def onchange_probation(self):
        if self.probation_id:
            hours_per_day = (
                self.resource_calendar_id
                and self.resource_calendar_id.hours_per_day
                or 8
            )
            wage_per_month = (self.probation_id.wage_per_hour * hours_per_day) * 30
            self.wage = wage_per_month


class SafetyDocument(models.Model):
    _name = "safety.document"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Safety Document"
    _rec_name = "doc_number"

    doc_number = fields.Char("Number", size=128)
    issue_place = fields.Char("Place of Issue", size=128)
    issue_date = fields.Date("Date of Issue", tracking=True)
    expiry_date = fields.Date("Date of Expiry", tracking=True)
    notes = fields.Text("Notes")
    attachment_ids = fields.Many2many("ir.attachment", string="Attachments")
    product_ids = fields.One2many(
        "product.template", "safety_document_id", string="Materials"
    )


class ProductTemplate(models.Model):
    _inherit = "product.template"

    safety_document_id = fields.Many2one("safety.document", string="Safety Document")

    def open_safety_document(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "hr_evolution.action_safety_document"
        )
        if self.safety_document_id:
            action["domain"] = [("id", "in", self.safety_document_id.ids)]
            action["views"] = [
                (
                    self.env.ref("hr_evolution.view_hr_safety_document").id,
                    "form",
                )
            ]
            action["res_id"] = self.safety_document_id.id
        return action
