# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        context = dict(self.env.context)
        if 'check_shop_equipment' in context:
            categories = self.env['maintenance.equipment.category'].search([('equipment_category_type', '=', 'shop')])
            equipments = self.env['maintenance.equipment'].search([('category_id', 'in', categories.ids)])
            args.append(('id', 'in', equipments.mapped('product_id').ids))
        return super(ProductProduct, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs):
        domain = domain or []
        context = dict(self.env.context)
        if 'check_shop_equipment' in context:
            categories = self.env['maintenance.equipment.category'].search([('equipment_category_type', '=', 'shop')])
            equipments = self.env['maintenance.equipment'].search([('category_id', 'in', categories.ids)])
            domain.append(('id', 'in', equipments.mapped('product_id').ids))
        return super(ProductProduct, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order, **read_kwargs)
