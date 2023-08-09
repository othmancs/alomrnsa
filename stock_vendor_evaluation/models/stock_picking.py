from odoo import fields, models, api
import logging
_logger = logging.getLogger(__name__)
from datetime import datetime, timedelta


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    evaluation_id = fields.Many2one('evaluation.criteria', copy=False)
    evaluation_value = fields.Float('Average', related='evaluation_id.value', group_operator='avg', store=True)

    def write(self, vals):
        """Update vendor rating."""
        res = super(StockPicking, self).write(vals)
        for record in self:
            picking_ids = self.env["stock.picking"].search([
                ('partner_id', '=', record.partner_id.id),
                ('evaluation_id', '!=', False),
                ('picking_type_code', '=', 'incoming'),
                ('state', 'not in', ['draft', 'waiting', 'cancel']),
                ('scheduled_date', '>', datetime.today() - timedelta(days=365))
            ])
            if picking_ids:
                values = picking_ids.mapped('evaluation_value')
                record.partner_id.write({
                    'vendor_rating': sum(values) / len(values)
                })
        return res
