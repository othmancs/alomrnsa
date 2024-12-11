# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrEndOfService(models.Model):
    _inherit = 'hr.end.service'

    unpaid_loan = fields.Float(string="Unpaid Loan", compute='_compute_unpaid_loan', stote=True, readonly=True)

    @api.depends("employee_id")
    def _compute_unpaid_loan(self):
        hr_loan_line_obj = self.env["hr.loan.line"]
        for end_service in self:
            loan_lines = hr_loan_line_obj.search(
                [('loan_id.state', '=', 'approve'), ('employee_id', '=', end_service.employee_id.id),
                 ('paid', '=', False)])
            end_service.unpaid_loan = sum(line.amount for line in loan_lines)
