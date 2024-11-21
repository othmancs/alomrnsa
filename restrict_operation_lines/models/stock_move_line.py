from odoo import models, fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    can_add_operation_lines = fields.Boolean(
        string='Can Add Operation Lines',
        compute='_compute_can_add_operation_lines',
        store=True
    )

    def _compute_can_add_operation_lines(self):
        for record in self:
            # Add your logic here
            record.can_add_operation_lines = True
