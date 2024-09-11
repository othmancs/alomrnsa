# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AnnualLeavingEmployees(models.TransientModel):
    _name = 'annual.leaving.employees'
    _description = 'Generate Annual Leaving Record for all selected employees'

    employee_ids = fields.Many2many('hr.employee', string='Employees', domain=lambda self: self._get_employee_domain())

    def _get_employee_domain(self):
        domain = []
        leave_allocation_obj = self.env['hr.leave.allocation']
        employees = leave_allocation_obj.search([('state', '=', 'validate'),('holiday_status_id.is_annual_leave', '=', True)]).mapped('employee_id')
        domain.append(('id', 'in', employees.ids))
        return domain

    def generate_records(self):
        for rec in self.employee_ids:
            ctx = self.env.context
            leaves_details_obj = self.env['leaves.details']
            leaves_details_ids = leaves_details_obj.search([('employee_id', '=', rec.id), ('annual_leaving_id', '=', ctx.get('active_id'))])
            if leaves_details_ids:
                raise ValidationError(_('You already done %s leaves details!!') % rec.name)
            else:
                leave_detail_id = self.env['leaves.details'].create({'employee_id': rec.id,
                                               'annual_leaving_id': ctx.get('active_id')
                    })
                leave_detail_id.onchange_employee()
