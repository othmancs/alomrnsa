from odoo import api, models, _, fields
from odoo.exceptions import UserError


class Invoice(models.Model):
    _inherit = 'account.move.line'

    readonly_price = fields.Boolean(string="Belongs to Group", compute='_compute_belongs_to_group')

    @api.depends('product_id')
    def _compute_belongs_to_group(self):
        for rec in self:
            rec.readonly_price = self.env.user.has_group('sb_group_access.cannot_edit_unit_price')

