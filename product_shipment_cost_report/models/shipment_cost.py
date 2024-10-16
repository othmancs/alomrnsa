from odoo import models, fields, api

class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    product_cost = fields.Float(string="Product Cost", compute="_compute_product_cost")

    @api.depends('picking_ids', 'cost_lines')
    def _compute_product_cost(self):
        for record in self:
            total_cost = 0.0
            for picking in record.picking_ids:
                for move_line in picking.move_lines:
                    total_cost += move_line.product_uom_qty * move_line.product_id.standard_price
            record.product_cost = total_cost
