# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrEndOfService(models.Model):
    _inherit = 'hr.end.service'

    no_closed_petty_cash = fields.Float(string="No Closed Petty Cash", compute='_compute_no_closed_petty_cash',
                                        stote=True,
                                        readonly=True)

    @api.depends("employee_id")
    def _compute_no_closed_petty_cash(self):
        petty_cash_obj = self.env["petty.cash"]
        for end_service in self:
            petty_cash_ids = petty_cash_obj.search(
                [('state', '!=', 'closed'), ('responsible_id.employee_id', '=', end_service.employee_id.id)])
            end_service.no_closed_petty_cash = sum(petty_cash.amount_total for petty_cash in petty_cash_ids)

    def action_approve(self):
        petty_cash_obj = self.env["petty.cash"]
        for end_service in self:
            if end_service.state != "in_progress":
                continue

            if petty_cash_obj.search_count(
                    [('state', '!=', 'closed'), ('responsible_id.employee_id', '=', end_service.employee_id.id)]) > 0:
                raise ValidationError(_('Cannot approve because employee have some petty cash not closed'))
            return super(HrEndOfService, self).action_approve()
