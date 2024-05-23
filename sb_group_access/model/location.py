from odoo import api, models, _
from odoo.exceptions import UserError


class Location(models.Model):
    _inherit = 'stock.location'

    @api.model_create_multi
    def create(self, vals_list):
        result = super(Location, self).create(vals_list)
        if self.env.user.has_group('sb_group_access.cannot_add_location'):
            raise UserError(_("You are not authorized to add location"))
        return result


    def write(self, vals_list):
        result = super(Location, self).write(vals_list)
        if self.env.user.has_group('sb_group_access.cannot_add_location'):
            raise UserError(_("You are not authorized to edit location"))
        return result
