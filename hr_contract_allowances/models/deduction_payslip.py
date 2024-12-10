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
            lone = self.env['contract.deduction.line'].search(
                [('date', '>=', res.get('date_from')), ('date', '<=', res.get('date_to')),
                 ('deduction_id.state', '=', 'approve'),
                 ('status', '=', 'pending'), ('employee_id', '=', int(res.get('employee_id')))])
            if lone:
                res['deduction_line_id'] = lone.ids
                res['deduction_amount'] = sum(x.amount for x in lone)
        return res

    # Fields declaration
    deduction_line_id = fields.Many2many('contract.deduction.line', 'contract_deduction_line_pay_rel', 'payslip_id', 'line_id',
                                    string="This Month Deduction")
    deduction_amount = fields.Float('Deduction Amount')

    # CRUD methods (and name_get, name_search, ...) overrides
    @api.model
    def create(self, val):
        if val.get('date_from') and val.get('employee_id'):
            deductions = self.env['contract.deduction.line'].search(
                [('date', '>=', val.get('date_from')), ('date', '<=', val.get('date_to')),
                 ('deduction_id.state', '=', 'approve'),
                 ('status', '=', 'pending'), ('employee_id', '=', int(val.get('employee_id')))])
            if deductions:
                val['deduction_line_id'] = [(6, 0, deductions.ids)]
                val['deduction_amount'] = sum(x.amount for x in deductions)
        return super(HrPayslip, self).create(val)

    # Action methods
    def action_payslip_done(self):
        """its inherited function. we add in to update status of Deduction lines"""
        res = super(HrPayslip, self).action_payslip_done()
        for rec in self:
            if rec.deduction_line_id:
                for line in rec.deduction_line_id:
                    line.update({
                        'status': 'done',
                        'payslip_id': rec.id,
                    })
        return res
