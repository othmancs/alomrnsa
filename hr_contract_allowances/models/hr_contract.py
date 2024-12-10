# -*- coding: utf-8 -*-

import logging
_logger = logging.getLogger(__name__)

from odoo import models, fields, api, exceptions
from odoo import tools, _
from odoo.tools import UserError


class Contract(models.Model):

    _inherit = 'hr.contract'

    @api.constrains('state')
    def _check_state(self):
        for record in self:
            if record.state == 'open':
                contract_ids = self.env['hr.contract'].search(
                    [('employee_id', '=', record.employee_id.id), ('state', '=', 'open')])
                if len(contract_ids) > 1:
                    raise exceptions.ValidationError(_('Employee Must Have Only One Running Contract'))

    basic_salary = fields.Float('Basic Salary')
    allowances_ids = fields.One2many(comodel_name="hr.contract.allowance.line", inverse_name="contract_id")
    deduction_ids = fields.One2many(comodel_name="hr.contract.deduction.line", inverse_name="deduction_contract_id")
    net_allowance = fields.Float('Total Allowance', compute='_get_net_allowance_amount', store=True)
    basic_allowance = fields.Float('Basic Allowance', compute='_get_net_allowance_amount', store=True)
    extra_allowance = fields.Float('Extra Allowance', compute='_get_net_allowance_amount', store=True)
    net_deduction = fields.Float('Total Deduction', compute='_get_net_deduction_amount', store=True)

    @api.onchange('net_allowance','net_deduction','basic_salary')
    def compute_wage(self):
        """
        calc wage for contract
        """
        for rec in self:
            rec.wage = rec.basic_salary + rec.net_allowance - rec.net_deduction

    @api.depends('allowances_ids')
    def get_all_allowances(self):
        """
        sum all allowances
        """
        return sum(self.allowances_ids.mapped('amount'))

    @api.depends('allowances_ids.amount')
    def _get_net_allowance_amount(self):
        """
        calc all allowance with specific basic and extra category
        """
        net_allowance = 0
        for record in self:
            basic = 0
            extra = 0
            for children in record.allowances_ids:
                if children.amount:
                    net_allowance += children.amount
                if children.category == 'basic':
                    basic = basic + children.amount
                else:
                    extra = extra + children.amount
            record.net_allowance = net_allowance
            record.basic_allowance = basic
            record.extra_allowance = extra

    @api.depends('deduction_ids.amount')
    def _get_net_deduction_amount(self):
        """
        it calc deduction of contract
        """
        net_deduction = 0
        for record in self:
            for children in record.deduction_ids:
                if children.amount:
                    net_deduction += children.amount
            record.net_deduction = net_deduction
