from odoo import api, models, _
from odoo.exceptions import UserError


class Operations(models.Model):
    _inherit = 'stock.picking.type'

    @api.model_create_multi
    def create(self, vals_list):
        # res = super(Operations, self).create(vals_list)
        if self.env.user.has_group('sb_group_access.cannot_add_operation'):
            raise UserError(_("You are not authorized to add operation"))
        return super(Operations, self).create(vals_list)

    def write(self, vals_list):
        res = super(Operations, self).write(vals_list)
        if self.env.user.has_group('sb_group_access.cannot_add_operation'):
            raise UserError(_("You are not authorized to edit operation"))
        return res
