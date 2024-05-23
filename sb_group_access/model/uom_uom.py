from odoo import api, models, _
from odoo.exceptions import UserError


class UnitOfMeasure(models.Model):
    _inherit = 'uom.uom'

    @api.model_create_multi
    def create(self, vals_list):
        res = super(UnitOfMeasure, self).create(vals_list)
        if self.env.user.has_group('sb_group_access.cannot_add_unit_of_measure'):
            raise UserError(_("You are not authorized to add unit of measure."))
        return res


    def write(self, vals_list):
        res = super(UnitOfMeasure, self).write(vals_list)
        if self.env.user.has_group('sb_group_access.cannot_add_unit_of_measure'):
            raise UserError(_("You are not authorized to edit unit of measure."))
        return res
