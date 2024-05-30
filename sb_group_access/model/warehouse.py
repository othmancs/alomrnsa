from odoo import api, models, _
from odoo.exceptions import UserError


class Warehouse(models.Model):
    _inherit = 'stock.warehouse'

    @api.model_create_multi
    def create(self, vals_list):
        res = super(Warehouse, self).create(vals_list)
        if self.env.user.has_group('sb_group_access.cannot_add_warehouse'):
            raise UserError(_("You are not authorized to add warehouse"))
        return res

    def write(self, vals_list):
        res = super(Warehouse, self).write(vals_list)
        if self.env.user.has_group('sb_group_access.cannot_add_warehouse'):
            raise UserError(_("You are not authorized to edit warehouse"))
        return res
