# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class EmployeeDependent(models.Model):
    _name = 'employee.dependent'
    _description = 'Employee dependent information'

    name = fields.Char('Name(As in Passport)', size=50, help="Name of the dependent", required=True)
    relation = fields.Selection([('child', 'Child'), ('spouse', 'Spouse')], 'Relation')
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, ondelete="cascade", default=lambda self: self.env['hr.employee'].get_employee())
    nationality = fields.Many2one('res.country', 'Nationality')
    birthdate = fields.Date("Date of Birth", required=True)
    dependent_type = fields.Selection([('employee', 'Employee'), ('family', 'Family'), ('new_born', 'New Born Baby')], 'Type', required=True, default='employee')
    document_ids = fields.One2many('res.documents', 'dependent_id', string='Document')

    @api.model
    def default_get(self, fields):
        """
            Override method for fetch default values
        """
        res = super(EmployeeDependent, self).default_get(fields)
        context = dict(self.env.context)
        if context.get('active_id'):
            employee = self.env['hr.employee'].browse(context['active_id'])
            if employee:
                res.update({'employee_id': employee.id})
        return res


class ResDocuments(models.Model):
    _inherit = 'res.documents'

    dependent_id = fields.Many2one('employee.dependent', string='Dependent')


class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    dependent_ids = fields.One2many('employee.dependent', 'employee_id', string='Dependents')
    dependent_count = fields.Integer(string='Total Dependents', compute='_compute_dependents')

    def _compute_dependents(self):
        """
            count dependents related employee
        """
        for employee in self:
            dependents = self.env['employee.dependent'].search([('employee_id', '=', employee.id)])
            employee.dependent_count = len(dependents) if dependents else 0

    def action_dependents(self):
        """
            Show employee Dependents
        """
        dependent_ids = self.env['employee.dependent'].search([('employee_id', '=', self.id)])
        action = self.env["ir.actions.actions"]._for_xml_id("saudi_hr_dependent.action_employee_dependent")
        if len(dependent_ids) > 1:
            action['domain'] = [('id', 'in', dependent_ids.ids)]
        elif len(dependent_ids) == 1:
            res = self.env.ref('saudi_hr_dependent.employee_dependent_view_form', False)
            action['views'] = [(res.id, 'form')]
            action['res_id'] = dependent_ids[0].id
        else:
            action['domain'] = [('id', 'in', dependent_ids.ids)]
        return action
