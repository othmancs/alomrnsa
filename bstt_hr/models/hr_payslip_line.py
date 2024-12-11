# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    partner_id = fields.Many2one('res.partner', related=False, compute="_compute_partner_id", store=True)

    @api.depends('salary_rule_id', 'employee_id')
    def _compute_partner_id(self):
        for line in self:
            if not line.employee_id.address_home_id:
                partner = self.env['res.partner'].create(
                    {'name': line.employee_id.name,
                     'street': line.employee_id.address or False,
                     })
                line.employee_id.address_home_id = partner.id
            partner = line.salary_rule_id.partner_id.id or line.employee_id.address_home_id.id
            line.partner_id = partner
