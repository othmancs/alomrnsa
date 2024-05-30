from odoo import api, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ProductTemplate, self).create(vals_list)
        if self.env.user.has_group('sb_group_access.cannot_add_product'):
            raise UserError(_("You are not authorized to create product."))
        return res

    def write(self, vals_list):
        res = super(ProductTemplate, self).write(vals_list)
        if self.env.user.has_group('sb_group_access.cannot_add_product'):
            raise UserError(_("You are not authorized to edit product."))
        return res
