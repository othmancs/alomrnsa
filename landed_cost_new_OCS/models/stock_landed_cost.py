from odoo import models, fields, api

class LandedCostLine(models.Model):
    _inherit = 'stock.landed.cost.lines'
    
    split_method = fields.Selection(
        selection_add=[('construction_costs', 'تكاليف العمران')],
        ondelete={'construction_costs': 'set default'}
    )
    
    @api.depends('price_unit', 'split_method', 'cost_id')
    def _compute_cost_lines(self):
        super(LandedCostLine, self)._compute_cost_lines()
        for line in self:
            if line.split_method == 'construction_costs':
                total_cost = line.cost_id.amount_total
                pickings = line.cost_id.picking_ids
                if pickings:
                    moves = pickings.mapped('move_lines')
                    purchase_lines = moves.mapped('purchase_line_id')
                    if purchase_lines:
                        total_purchase_cost = sum(purchase_lines.mapped('price_unit'))
                        if total_purchase_cost != 0:
                            percentage = total_cost / total_purchase_cost
                            line.price_unit = line.product_id.standard_price * percentage