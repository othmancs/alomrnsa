# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models, api, _


class Product(models.Model):
    _inherit = 'product.template'

    warranty_id = fields.Many2one('warranty.template', string="Warranty Template")


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        context = self._context or {}
        if 'sale_line_id' in context:
            sale_line_id = self.env['sale.order.line'].browse(context.get('sale_line_id', 0))
            if sale_line_id:
                args.append(('id', 'in', sale_line_id.product_id.ids))
            else:
                args.append(('tracking', '=', 'serial'))
        return super(ProductProduct, self)._name_search(name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        context = self._context or {}
        domain = domain or []
        if 'sale_line_id' in context:
            sale_line_id = self.env['sale.order.line'].browse(context.get('sale_line_id', 0))
            if sale_line_id:
                domain += [('id', 'in', sale_line_id.product_id.ids)]
            else:
                domain += [('tracking', '=', 'serial')]
        return super(ProductProduct, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
