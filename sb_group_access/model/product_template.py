from odoo import api, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.user.has_group('sb_group_access.can_add_product'):
            raise UserError(_("You are not authorized to create product."))
        return super(ProductTemplate, self).create()
