from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockPickingSecurity(models.Model):
    _inherit = 'stock.picking'

    is_line_creation_allowed = fields.Boolean(
        compute='_compute_is_line_creation_allowed',
        store=False
    )

    @api.depends('state')
    def _compute_is_line_creation_allowed(self):
        for picking in self:
            if self.env.user.has_group('sb_group_access.group_inv_transfer_add_line'):
                # Allow creation only if state is 'draft'
                picking.is_line_creation_allowed = picking.state == 'draft'
            else:
                # If the user is not in the group, always allow line creation
                picking.is_line_creation_allowed = True

    @api.model
    def write(self, vals):
        if 'move_ids_without_package' in vals and self.state != 'draft':
            # Check if user has the specific group permissions
            if not self.env.user.has_group('sb_group_access.group_inv_transfer_add_line'):
                # Check for new line additions in move_ids_without_package
                new_lines = vals.get('move_ids_without_package', [])
                if isinstance(new_lines, list) and any(line[0] == 0 for line in new_lines):
                    raise UserError(_("لا يمكنـك إضــافـة أصنــاف أخــرى"))
        return super(StockPickingSecurity, self).write(vals)
