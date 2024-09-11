# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError
import time


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def action_view_equipment(self):
        emp_reg_id = self.env['hr.employee.registration'].search([('employee_id', '=',self.id)])
        action = self.env["ir.actions.actions"]._for_xml_id("saudi_hr_it_operations.action_equipment_registration")
        it_dept_ids = emp_reg_id and emp_reg_id.it_dept_ids and emp_reg_id.it_dept_ids.ids or []
        action['domain'] = [('id', 'in', it_dept_ids)]
        return action

    equipment_registrations = fields.Many2many('equipment.registration', 'IT Equipments',
        compute="_compute_equipment_registration")

    def _compute_equipment_registration(self):
        for rec in self:
            emp_reg_id = self.env['hr.employee.registration'].search([('employee_id', '=', rec.id)])
            rec.equipment_registrations = []
            if emp_reg_id:
                it_dept_ids = emp_reg_id and emp_reg_id.it_dept_ids and emp_reg_id.it_dept_ids.ids or []
                rec.equipment_registrations = [(6, 0, it_dept_ids)]


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_equipment = fields.Boolean(string='Has Equipment', default=False)
