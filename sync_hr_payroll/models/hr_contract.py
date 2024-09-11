# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrContract(models.Model):
    _inherit = 'hr.contract'
    _description = 'Employee Contract'

    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure')
    schedule_pay = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi-annually', 'Semi-annually'),
        ('annually', 'Annually'),
        ('weekly', 'Weekly'),
        ('bi-weekly', 'Bi-weekly'),
        ('bi-monthly', 'Bi-monthly'),
    ], string='Scheduled Pay', index=True, default='monthly',
    help="Defines the frequency of the wage payment.")
    resource_calendar_id = fields.Many2one(required=True, help="Employee's working schedule.")

    hra_allow = fields.Selection([
        ('fixed_amount', 'Fixed Amount'),
        ('percentage', 'Percentage')], default='fixed_amount',
        string="House Rent Allowance")
    hra_fixed_amt = fields.Float(string='Fixed Amount', default=0.0)
    hra_per = fields.Float(string='Percentage (%)', default=0.0)

    trans_allow = fields.Selection([
        ('fixed_amount', 'Fixed Amount'),
        ('percentage', 'Percentage')], default='fixed_amount',
        string="Transportation Allowance")
    tra_fixed_amt = fields.Float(string='Fixed Amount', default=0.0)
    tra_per = fields.Float(string='Percentage (%)', default=0.0)

    con_allow = fields.Selection([
        ('fixed_amount', 'Fixed Amount'),
        ('percentage', 'Percentage')], default='fixed_amount',
        string="Conveyance Allowance")
    con_fixed_amt = fields.Float(string='Fixed Amount', default=0.0)
    con_per = fields.Float(string='Percentage (%)', default=0.0)

    meal_fixed_amt = fields.Float(string='Meal Allowance Fixed Amount', default=0.0)

    congravie_fixed_amt = fields.Float(string='Conveyance Allowance For Gravie Fixed Amount', default=0.0)

    @api.constrains('hra_per')
    def _check_hra_per(self):
        for contract in self:
            if contract.hra_per > 100 or contract.hra_per < 0:
                raise ValidationError(_('The value of House Rent Allowance percentage must be between 1 to 100.'))

    @api.constrains('tra_per')
    def _check_tra_per(self):
        for contract in self:
            if contract.tra_per > 100 or contract.tra_per < 0:
                raise ValidationError(_('The value of Transportation Allowance percentage must be between 1 to 100.'))

    @api.constrains('con_per')
    def _check_con_per(self):
        for contract in self:
            if contract.con_per > 100 or contract.con_per < 0:
                raise ValidationError(_('The value of Conveyance Allowance percentage must be between 1 to 100.'))

    @api.onchange('hra_allow')
    def hra_allow_onchange(self):
        for contract in self:
            if contract.hra_allow == 'fixed_amount':
                contract.hra_per = 0.0
                contract.write({'hra_per': 0.0})
            else:
                contract.hra_fixed_amt = 0.0

    @api.onchange('trans_allow')
    def trans_allow_onchange(self):
        for contract in self:
            if contract.trans_allow == 'fixed_amount':
                contract.tra_per = 0.0
            else:
                contract.tra_fixed_amt = 0.0

    @api.onchange('con_allow')
    def con_allow_onchange(self):
        for contract in self:
            if contract.con_allow == 'fixed_amount':
                contract.con_per = 0.0
            else:
                contract.con_fixed_amt = 0.0

    def get_all_structures(self):
        structures = self.mapped('struct_id')
        if not structures:
            return []
        return list(set(structures._get_parent_structure().ids))

    def get_attribute(self, code, attribute):
        return self.env['hr.contract.advantage.template'].search([('code', '=', code)], limit=1)[attribute]

    def set_attribute_value(self, code, active):
        for contract in self:
            if active:
                value = self.env['hr.contract.advantage.template'].search([('code', '=', code)], limit=1).default_value
                contract[code] = value
            else:
                contract[code] = 0.0


class HrContractAdvantageTemplate(models.Model):
    _name = 'hr.contract.advantage.template'
    _description = "Employee's Advantage on Contract"

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    lower_bound = fields.Float('Lower Bound', help="Lower bound authorized by the employer for this advantage")
    upper_bound = fields.Float('Upper Bound', help="Upper bound authorized by the employer for this advantage")
    default_value = fields.Float('Default value for this advantage')
