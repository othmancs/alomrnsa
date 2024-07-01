from odoo import api, models, _
from odoo.exceptions import UserError


class ProductCategory(models.Model):
    _inherit = 'product.category'

    @api.model
    def create(self, name):
        result = super(ProductCategory, self).create(name)
        if self.env.user.has_group('sb_group_access.cannot_add_product_category'):
            raise UserError(_("You are not authorized to create product category."))
        return result

    def write(self, name):
        result = super(ProductCategory, self).write(name)
        if self.env.user.has_group('sb_group_access.cannot_add_product_category'):
            raise UserError(_("You are not authorized to edit product category."))
        return result
