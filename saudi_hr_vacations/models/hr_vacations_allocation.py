# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class HrVacationsAllocation(models.Model):
    _name = "hr.vacations.allocation"
    _description = "HR Vacations Allocation"

    name = fields.Char(string="Name", required=True)
    employee_id = fields.Many2one("hr.employee", string="Employee")
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    state = fields.Selection(
        [
            ("draft", "To Submit"),
            ("confirm", "To Approve"),
            ("refuse", "Refuse"),
            ("validate", "Approved"),
            ("cancel", "Cancel"),
        ],
        default="draft",
        string="State",
    )
    duration = fields.Integer(string="Duration")
    contract_id = fields.Many2one("hr.contract", string="Contract")
    remaining_duration = fields.Integer(
        string="Remaining Duration", compute="compute_remaining_duration"
    )

    def confirm(self):
        self.state = "confirm"

    def approve(self):
        self.state = "validate"

    def refuse(self):
        self.state = "refuse"

    def cancel(self):
        self.state = "cancel"

    def compute_remaining_duration(self):
        vacation = self.env["hr.vacation"]
        for rec in self:
            rec.remaining_duration = rec.duration
            requested_vacations = vacation.search(
                [
                    ("date_start", ">", rec.from_date),
                    ("date_to", "<", rec.to_date),
                    ("employee_id", "=", rec.employee_id.id),
                ]
            )
            if rec.from_date and rec.to_date and requested_vacations:
                vacation_days = sum(
                    [(req.date_to - req.date_start).days for req in requested_vacations]
                )
                rec.remaining_duration = rec.duration - vacation_days

    @api.constrains("from_date", "to_date")
    def check_date(self):
        for rec in self:
            if rec.from_date > rec.to_date:
                raise UserError("End Date must be greater than of Start Date.")
