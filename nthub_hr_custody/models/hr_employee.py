# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.osv import expression


class Employee(models.Model):
    _inherit = 'hr.employee'

    custody_count = fields.Integer(compute='_custody_count', string='# Custody')
    equipment_count = fields.Integer(compute='_equipment_count', string='# Equipments')
    project_id = fields.Many2one('hr.employee','Project')
    related_partner = fields.Many2one('res.partner')

    # count of all custody contracts

    @api.model
    def create(self, vals):
        res = super(Employee, self).create(vals)
        if 'project_id' in vals:
            project_id = vals.get("project_id")
            self.change_projects_linked_to_custody(project_id)
        return res

    def write(self, vals):
        if 'project_id' in vals:
            project_id = vals.get("project_id")
            self.change_projects_linked_to_custody(project_id)

        return super(Employee, self).write(vals)

    def _custody_count(self):
        for each in self:
            custody_ids = self.env['hr.custody'].search([('employee', '=', each.id)])
            each.custody_count = len(custody_ids)

    # count of all custody contracts that are in approved state

    def custody_view(self):
        for each1 in self:
            custody_obj = self.env['hr.custody'].search([('employee', '=', each1.id)])
            custody_ids = []
            for each in custody_obj:
                custody_ids.append(each.id)
            view_id = self.env.ref('nthub_hr_custody.hr_custody_form_view').id
            if custody_ids:
                if len(custody_ids) <= 1:
                    value = {
                        'view_mode': 'form',
                        'res_model': 'hr.custody',
                        'view_id': view_id,
                        'type': 'ir.actions.act_window',
                        'name': _('Custody'),
                        'res_id': custody_ids and custody_ids[0]
                    }
                else:
                    value = {
                        'domain': str([('id', 'in', custody_ids)]),
                        'view_mode': 'tree,form',
                        'res_model': 'hr.custody',
                        'view_id': False,
                        'type': 'ir.actions.act_window',
                        'name': _('Custody'),

                    }

                return value

    def action_generate_custody(self):
        property_ids = self.job_id.property_ids
        vals = {
            'employee': self.id,
            'date_request': fields.Date.today(),
            'return_date': fields.Date.today(),
            'purpose': 'New Position Custody',
            'property_ids': [],
        }
        for property_id in property_ids:
            vals['property_ids'].append((0, 0, {
                'product_id': property_id.product_id.id,
                'quantity': property_id.quantity,
                'name': property_id.name,
                'uom': property_id.uom.id,

            },
                                         ))

        self.env['hr.custody'].sudo().create(vals)

    def change_projects_linked_to_custody(self, project_id):
        custodies = self.env['hr.custody'].sudo().search(
            [('employee', '=', self.id), ('state', 'in', ['approved', 'to_approve_return'])])
        param = self.env['ir.config_parameter'].sudo()
        location_id = int(param.get_param('nthub_hr_custody.destination_location'))
        for custody in custodies:
            for property in custody.property_ids:
                if self.update_or_create_quant(property, location_id, project_id):
                    custody.project_id = project_id

    def update_or_create_quant(self, property, location_id, project_id):
        domain = [('product_id', '=', property.product_id.id), ('location_id', '=', location_id)]
        if property.lot_id:
            domain = expression.AND([[('lot_id', '=', property.lot_id.id)], domain])
        if self.analytic_account_id:
            domain = expression.AND([[('project_id', '=', self.project_id.id)], domain])
        quant_pre = self.env['stock.quant'].sudo().search(domain)
        if quant_pre:
            quant_pre.quantity -= property.delivered
            domain2 = [('product_id', '=', property.product_id.id), ('location_id', '=', location_id)]
            if property.lot_id:
                domain2 = expression.AND([[('lot_id', '=', property.lot_id.id)], domain2])
            if self.analytic_account_id:
                domain2 = expression.AND([[('project_id', '=', project_id)], domain2])
            quant_post = self.env['stock.quant'].sudo().search(domain2)
            if quant_post:
                quant_post.quantity += property.delivered
            else:
                vals = {
                    'location_id': quant_pre.location_id.id,
                    'product_id': quant_pre.product_id.id,
                    'lot_id': quant_pre.lot_id.id,
                    'owner_id': quant_pre.owner_id.id,
                    'project_id': project_id,
                    'quantity': property.delivered,

                }
                self.env['stock.quant'].create(vals)
            return True
        else:
            return False
