from odoo import api, models, _
from odoo.exceptions import UserError


class ProductCategory(models.Model):
    _inherit = 'product.category'

    @api.model
    def name_create(self, name):
        if not self.env.user.has_group('sb_group_access.can_add_product_category'):
            raise UserError(_("You are not authorized to create product category."))
        return super(ProductCategory, self).name_create()
