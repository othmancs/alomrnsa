# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    deduction_count = fields.Integer(string="Deduction Count", compute='_compute_employee_deduction')
    allowance_count = fields.Integer(string="Loan Count", compute='_compute_employee_allowance')

    @api.depends('name')
    def _compute_employee_deduction(self):
        """This compute the total deduction_count of an employee.
            """
        for rec in self:
            rec.deduction_count = self.env['contract.deduction'].search_count([('employee_id', '=', rec.id)])

    @api.depends('name')
    def _compute_employee_allowance(self):
        """This compute the total deduction_count of an employee.
            """
        for rec in self:
            rec.allowance_count = self.env['contract.allowance'].search_count([('employee_id', '=', rec.id)])

    def show_deductions(self):
        return {
            'name': _('Employee Deduction'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'contract.deduction',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('employee_id', '=', self.ids)],
        }

    def show_allowances(self):
        return {
            'name': _('Employee Allowances'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'contract.allowance',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('employee_id', '=', self.ids)],
        }