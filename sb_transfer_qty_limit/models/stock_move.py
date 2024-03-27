from odoo import api, fields, models
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.onchange('quantity_done')
    def onchange_quantity_done(self):
        for rec in self:
            if rec.quantity_done != rec.product_uom_qty:
                # raise ValidationError('Done amount can't be more than the Demand')
                raise ValidationError('لا يمكن استلام كميه اكثر من المطلوبه')
