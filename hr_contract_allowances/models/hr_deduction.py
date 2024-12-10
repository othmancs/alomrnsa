# -*- coding: utf-8 -*-

import logging
_logger = logging.getLogger(__name__)

from odoo import models, fields, api, exceptions
from odoo import tools, _
from odoo.tools import UserError
DEFAULT_RULE_PYTHON_CODE = """
total = 0
for line in contract.deduction_ids:
    if line.deduction_id.name == '%s':
        total = line.amount
    result = total
"""


class Deduction(models.Model):
    _name = 'hr.deduction'
    _rec_name = 'name'
    _description = 'Deduction'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Deduction Name", required=True)
    python_code = fields.Text(string="Python Code", compute="_compute_python_code")
    active = fields.Boolean(string="Active", default=True)

    @api.depends('name')
    def _compute_python_code(self):
        """
                it generates python code for deduction
                """
        for rec in self:
            rec.python_code = DEFAULT_RULE_PYTHON_CODE % rec.name

    def unlink(self):
        """restrict on delete
                        """
        for record in self:
            contract_lines = self.env['hr.contract.deduction.line'].search_count([('deduction_id', '=', record.id)])
            if contract_lines != 0:
                raise exceptions.ValidationError(
                    _('You can not delete the Deduction which is used in employee contracts'))
        res = super(Deduction, self).unlink()
        return res

    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)', 'Deduction Rule with name already created !')
    ]


class ContractDeductionLine(models.Model):
    _name = 'hr.contract.deduction.line'
    _rec_name = 'deduction_id'
    _description = 'Contract Deduction Line'

    deduction_id = fields.Many2one(comodel_name="hr.deduction", string="Deduction")
    deduction_contract_id = fields.Many2one(comodel_name="hr.contract", string="Contract")
    rate = fields.Float('Rate/Amount')
    type = fields.Selection([('Amount', 'Amount'),
                             ('Percentage', 'Percentage')], string='Type', default='Amount')
    amount = fields.Float(string="Amount", compute='_get_amount', store=True)
    index_value = fields.Char(string="Index")

    def create(self, values):
        record = super(ContractDeductionLine, self).create(values)
        return record

    @api.depends('type', 'rate', 'deduction_contract_id.basic_salary')
    def _get_amount(self):
        """
               it calc total amount according to formula
               """
        for record in self:
            if record.type == 'Amount':
                record.amount = record.rate
            else:
                if record.deduction_contract_id:
                    record.amount = record.deduction_contract_id.basic_salary * record.rate / 100
                else:
                    record.amount = record.rate / 100

    @api.constrains('deduction_id', 'deduction_contract_id')
    def check_unique_contract(self):
        for record in self:
            Records = self.search(
                [('deduction_id', '=', record.deduction_id.id), ('deduction_contract_id', '=', record.deduction_contract_id.id)])
            if len(Records) > 1:
                raise UserError(
                    str(self.deduction_id.name) + " has already been used for this contract !\nCan't add it twice")