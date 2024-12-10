# -*- coding: utf-8 -*-

import logging
_logger = logging.getLogger(__name__)

from odoo import models, fields, api, exceptions
from odoo import tools, _
from odoo.tools import UserError

DEFAULT_RULE_PYTHON_CODE = """
total = 0
for line in contract.allowances_ids:
    if line.allowance_id.name == '%s':
        total = line.amount
    result = total
"""


class Allowance(models.Model):
    _name = 'hr.allowance'
    _rec_name = 'name'
    _description = 'Allowance'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Allowance Name", required=True)
    python_code = fields.Text(string="Python Code", compute="_compute_python_code")
    active = fields.Boolean(string="Active", default=True)
    type = fields.Selection([('Amount', 'Amount'),
                             ('Percentage', 'Percentage')], string='Type', default='Amount')
    rate = fields.Float('Rate/Amount')
    min_fix_amount = fields.Float(string="Minimum Amount")
    max_fix_amount = fields.Float(string="Maximum Amount")
    # min_percentage_amount = fields.Float(string="Minimum Amount(%)")
    # max_percentage_amount = fields.Float(string="Maximum Amount(%)")


    @api.depends('name')
    def _compute_python_code(self):
        """
        it generates python code for allowance
        """
        for rec in self:
            rec.python_code = DEFAULT_RULE_PYTHON_CODE % rec.name

    def unlink(self):
        """restrict on delete
                """
        for record in self:
            contract_lines = self.env['hr.contract.allowance.line'].search_count([('allowance_id', '=', record.id)])
            if contract_lines != 0:
                raise exceptions.ValidationError(
                    _('You can not delete the allowance which is used in employee contracts'))
        res = super(Allowance, self).unlink()
        return res

    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)', 'Allowance Rule with name already created !')
    ]


class ContractAllowanceLine(models.Model):
    _name = 'hr.contract.allowance.line'
    _rec_name = 'allowance_id'
    _description = 'Contract Allowance Line'

    allowance_id = fields.Many2one(comodel_name="hr.allowance", string="Allowance")
    contract_id = fields.Many2one(comodel_name="hr.contract", string="Contract")
    rate = fields.Float('Rate/Amount')
    type = fields.Selection([('Amount', 'Amount'),
                             ('Percentage', 'Percentage')], string='Type', default='Amount')

    category = fields.Selection([('basic', 'Basic'),
                             ('allowance1', 'Allowance 1'),('allowance2', 'Other Allowance 2')], string='Category', default='basic')
    amount = fields.Float(string="Amount", compute='_get_amount', store=True)
    index_value = fields.Char(string="Index")
    # min_amoutn = fields.Float(string="Minimum Amoutn", compute='_get_amount', store=True)
    # max_amount = fields.Float(string="Max Amount", compute='_get_amount', store=True)

    #onchange allowance to get data from allowances..!
    @api.onchange('allowance_id','type')
    def _onchange_allowance_id(self):
        for data in self:
            if data.allowance_id and data.type:
                data.type = data.allowance_id.type
                data.rate = data.allowance_id.rate

    def create(self, values):
        record = super(ContractAllowanceLine, self).create(values)
        return record

    @api.depends('type', 'rate', 'contract_id.basic_salary')
    def _get_amount(self):
        """
        it calc total amount according to formula
        """
        for record in self:
            if record.type == 'Amount':
                record.amount = record.rate
            else:
                if record.contract_id:
                    record.amount = record.contract_id.basic_salary * record.rate / 100
                    if record.allowance_id.min_fix_amount or record.allowance_id.max_fix_amount:
                        if record.allowance_id.min_fix_amount and record.amount < record.allowance_id.min_fix_amount:
                            record.amount = record.allowance_id.min_fix_amount
                        elif record.allowance_id.max_fix_amount and record.amount > record.allowance_id.max_fix_amount:
                            record.amount = record.allowance_id.max_fix_amount
                        else:
                            record.amount = record.contract_id.basic_salary * record.rate / 100
                else:
                    record.amount = record.rate / 100
            # record.amount = record.min_amoutn = record.max_amount
            # record.amount = 5

    @api.constrains('allowance_id', 'contract_id')
    def check_unique_contract(self):
        for record in self:
            Records = self.search([('allowance_id', '=', record.allowance_id.id), ('contract_id', '=', record.contract_id.id)])
            if len(Records) > 1:
                raise UserError(str(self.allowance_id.name) + " has already been used for this contract !\nCan't add it twice")

    #constrains to apply validation
    @api.constrains('rate')
    def constrains_rate(self):
        for data in self:
            if data.rate and data.allowance_id and data.amount:
                if data.allowance_id.min_fix_amount:
                    if data.amount < data.allowance_id.min_fix_amount:
                        raise UserError(_("Amount can not be set less than %s")%(str(data.allowance_id.min_fix_amount)))
                if data.allowance_id.max_fix_amount:
                    if data.amount > data.allowance_id.max_fix_amount:
                        raise UserError(_("Amount can not be set more than %s")%(str(data.allowance_id.max_fix_amount)))
                # if not data.allowance_id.min_fix_amount or not data.allowance_id.max_fix_amount:
                #     raise UserError(_( "Please Configure Min and Max Amount in Allowances"))
                # if data.amount < data.allowance_id.min_fix_amount or data.amount > data.allowance_id.max_fix_amount:
                #     raise UserError(_( "Amount Should not Exit Between min and max amoutn given in Allowances..."))

            # if data.allowance_id and data.allowance_id.type == 'Percentage':
            #     if data.rate and data.contract_id.basic_salary:
            #         min_amount = ((data.contract_id.basic_salary * data.allowance_id.min_percentage_amount) / 100)
            #         max_amount = ((data.contract_id.basic_salary * data.allowance_id.max_percentage_amount) / 100)
            #         if not data.allowance_id.min_percentage_amount or not data.allowance_id.max_percentage_amount:
            #             raise UserError(_( "Please Configure Min and Max Amount(%) in Allowances"))
            #         if data.rate < min_amount or data.rate > max_amount:
            #             raise UserError(_( "Amount Should not Exit Between min and max amoutn given in Allowances..."))