from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    actual_destination_id = fields.Many2one(
        'stock.location', "Actual Dest Location",
        check_company=True, readonly=True, required=True,
        states={'draft': [('readonly', False)]})

    transit_transfer = fields.Many2one('stock.picking')

    def button_validate(self):
        for rec in self:
            result = super().button_validate()
            if rec.state == 'done' and rec.picking_type_code == 'internal' and not rec.transit_transfer:
                move_ids_without_package_vals = []

                created = self.env['stock.picking'].create({
                    'partner_id': rec.partner_id.id,
                    'picking_type_id': rec.picking_type_id.id,
                    'location_id': rec.location_dest_id.id,
                    'location_dest_id': rec.actual_destination_id.id,
                    'company_id': rec.company_id.id,
                    'transit_transfer': rec.id,
                })
                # Extract product_id and quantity from move_ids
                for move in rec.move_ids_without_package:
                    move_ids_without_package_vals.append((0, 0, {
                        'name': created.name,
                        'product_id': move.product_id.id,
                        'product_uom_qty': move.product_uom_qty,
                        'location_id': rec.location_dest_id.id,
                        'location_dest_id': rec.actual_destination_id.id,
                        'picking_id': created.id,

                    }))
                created.move_ids_without_package = move_ids_without_package_vals

            return result
