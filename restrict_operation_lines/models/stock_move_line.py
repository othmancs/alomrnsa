from odoo import models, api, exceptions, _

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.model
    def create(self, vals):
        # Check if the user is in the group
        if not self.env.user.has_group('restrict_operation_lines.group_restrict_add_operation_lines'):
            raise exceptions.AccessError(
                _("You do not have the necessary rights to add operation lines.")
            )
        return super(StockMoveLine, self).create(vals)
