from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    actual_destination_id = fields.Many2one(
        'stock.location', "Actual Dest Location",
        check_company=True, readonly=True, required=True,
        states={'draft': [('readonly', False)]})

    transit_transfer = fields.Many2one('stock.picking', copy=False)

    is_transit = fields.Boolean('Internal Transfer')

    @api.onchange('is_transit')
    def onchange_is_transit(self):
        for rec in self:
            rec.location_dest_id = False
            company_id = self.env.company.id
            if rec.is_transit:
                related_locations = self.env['stock.location'].search([
                    ('is_transit_location', '=', True),
                    '|', ('company_id', '=', False),
                    ('company_id', '=', company_id)
                ])
                return {'domain': {'location_dest_id': [
                    ('id', 'in', related_locations.ids)
                ]}}
            return {'domain': {'location_dest_id': [('company_id', 'in', (company_id, False))]}}

    def button_validate(self):
        for rec in self:
            result = super().button_validate()
            if rec.state == 'done' and rec.picking_type_code == 'internal' and not rec.transit_transfer and rec.is_transit:
                move_ids_without_package_vals = []
                operation_type = self.env['stock.picking.type'].search([
                    ('code', '=', 'internal'),
                    ('default_location_src_id', '=', rec.actual_destination_id.id)
                ])
                created = self.env['stock.picking'].create({
                    'partner_id': rec.partner_id.id,
                    'picking_type_id': operation_type.id,
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
