from odoo import api, models, _
from odoo.exceptions import UserError


class Product(models.Model):
    _inherit = 'product.product'

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.user.has_group('sb_group_access.cannot_add_product'):
            raise UserError(_("You are not authorized to create product."))
        return super(Product, self).create()
