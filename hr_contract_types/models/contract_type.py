# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ContractType(models.Model):
    _name = 'hr.contract.type'
    _description = 'Contract Type'
    _order = 'sequence, id'
    sequence = fields.Integer(string='Sequence', default=10)

    name = fields.Char(string='Contract Type', required=True, help="Name")

class HRContract(models.Model):
    _name = 'hr.contract'
    _inherit = ['mail.thread', 'hr.contract']
    schedule_pay = fields.Selection(related='structure_type_id.default_struct_id.schedule_pay', string="Schedule Pay", store=True)
    schedule_pay = fields.Selection([
        ('monthly', 'Monthly'),
        ('bi-weekly', 'Bi-Weekly'),
        ('weekly', 'Weekly'),
    ], string="Schedule Pay")
    
class ContractInherit(models.Model):
    _inherit = 'hr.contract'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of Contract.", default=10)

    type_id = fields.Many2one('hr.contract.type', string="Employee Category",
                              required=True, help="Employee category",
                              default=lambda self: self.env['hr.contract.type'].search([], limit=1))
    schedule_pay = fields.Selection(related='structure_type_id.default_struct_id.schedule_pay', string="Schedule Pay", store=True)
    schedule_pay = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly')
    ], string='Schedule Pay', default='monthly')
