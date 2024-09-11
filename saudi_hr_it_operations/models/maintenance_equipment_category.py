# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class MaintenanceEquipmentCategory(models.Model):
    _name = 'maintenance.equipment.category'
    _inherit = ['maintenance.equipment.category']
    _parent_name = 'parent_id'
    _rec_name = 'complete_name'
    _order = 'complete_name'

    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name', recursive=True,
        store=True)
    parent_id = fields.Many2one('maintenance.equipment.category', 'Parent Category', index=True, ondelete='cascade')
    child_id = fields.One2many('maintenance.equipment.category', 'parent_id', 'Child Categories')
    equipment_category_type = fields.Selection([('office', 'Office'), ('shop', 'Shop')], string='Category Type')

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive categories.'))
