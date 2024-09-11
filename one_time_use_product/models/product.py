# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_one_time_use = fields.Boolean(string="One Time Use dfdfd", default=False, help="Consider as one time use product")

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        """
            Override method for apply domain on product
        """
        context = dict(self.env.context)
        # if context.get('from_sale'):
        if context:
            product_ids = self.search([('is_one_time_use', '=', True)]).filtered(lambda l: l.qty_available <= 0)
            args.append(('id', 'not in', product_ids.ids))

        res = super(ProductProduct, self)._name_search(name, args=args, operator='ilike', limit=100, name_get_uid=None)
        return res

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        context = dict(self.env.context)
        # if context.get('from_sale'):
        if context:
            product_ids = self.search([('is_one_time_use', '=', True)]).filtered(lambda l: l.qty_available <= 0)
            domain = [('id', 'not in', product_ids.ids)]
        return super(ProductProduct, self).search_read(domain, fields, offset, limit, order)
