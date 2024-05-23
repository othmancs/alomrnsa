from odoo import api, models, _
from odoo.exceptions import UserError


class ProductCategory(models.Model):
    _inherit = 'product.category'

    @api.model
    def name_create(self, name):
        result = super(ProductCategory, self).name_create(name)
        if self.env.user.has_group('sb_group_access.cannot_add_product_category'):
            raise UserError(_("You are not authorized to create product category."))
        return result
