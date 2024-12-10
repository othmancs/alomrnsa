# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrPayslip(models.Model):
    # Private attributes
    _inherit = 'hr.payslip'

    # Default methods
    @api.model
    def default_get(self, fields):
        """it'll give you all loan line which is in given time interval of payslip"""
        res = super(HrPayslip, self).default_get(fields)
        if res.get('date_from') and res.get('employee_id'):
            lone = self.env['contract.allowance.line'].search(
                [('date', '>=', res.get('date_from')), ('date', '<=', res.get('date_to')),
                 ('allowance_id.state', '=', 'approve'),
                 ('status', '=', 'pending'), ('employee_id', '=', int(res.get('employee_id')))])
            if lone:
                res['allowance_line_id'] = lone.ids
                res['allowance_amount'] = sum(x.amount for x in lone)
        return res

    # Fields declaration
    allowance_line_id = fields.Many2many('contract.allowance.line', 'contract_allowance_line_pay_rel', 'payslip_id', 'line_id',
                                    string="This Month Allowance")
    allowance_amount = fields.Float('Allowance Amount')

    # CRUD methods (and name_get, name_search, ...) overrides
    @api.model
    def create(self, val):
        if val.get('date_from') and val.get('employee_id'):
            allowances = self.env['contract.allowance.line'].search(
                [('date', '>=', val.get('date_from')), ('date', '<=', val.get('date_to')),
                 ('allowance_id.state', '=', 'approve'),
                 ('status', '=', 'pending'), ('employee_id', '=', int(val.get('employee_id')))])
            if allowances:
                val['allowance_line_id'] = [(6, 0, allowances.ids)]
                val['allowance_amount'] = sum(x.amount for x in allowances)
        return super(HrPayslip, self).create(val)

    # Action methods
    def action_payslip_done(self):
        """its inherited function. we add in to update status of Allowance lines"""
        res = super(HrPayslip, self).action_payslip_done()
        for rec in self:
            if rec.allowance_line_id:
                for line in rec.allowance_line_id:
                    line.update({
                        'status': 'done',
                        'payslip_id': rec.id,
                    })
        return res
