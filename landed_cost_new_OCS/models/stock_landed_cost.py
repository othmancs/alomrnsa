from odoo import models, fields, api
from odoo.tools.float_utils import float_round
from collections import defaultdict

class LandedCostLine(models.Model):
    _inherit = 'stock.landed.cost.lines'

    percentage = fields.Float(
        string="النسبة المئوية", 
        compute='_compute_percentage', 
        store=True, 
        digits=(16, 2)
    )

    split_method = fields.Selection(
        selection_add=[('construction_costs', 'تكاليف العمران')],
        ondelete={'construction_costs': 'set default'},
        default='by_quantity'
    )

    @api.depends('cost_id.amount_total', 'cost_id.picking_ids')
    def _compute_percentage(self):
        for line in self:
            if line.split_method == 'construction_costs':
                total_costs = line.cost_id.amount_total
                pickings = line.cost_id.picking_ids

                if pickings:
                    total_purchase_cost = sum(
                        move.purchase_line_id.price_unit * move.purchase_line_id.product_qty 
                        * (move.purchase_line_id.currency_id.rate if move.purchase_line_id.currency_id != move.purchase_line_id.company_id.currency_id else 1)
                        for move in pickings.move_ids
                        if move.purchase_line_id and move.purchase_line_id.price_unit and move.purchase_line_id.product_qty
                    )

                    line.percentage = (total_costs / total_purchase_cost) * 100 if total_purchase_cost != 0 else 0.0
                else:
                    line.percentage = 0.0
            else:
                line.percentage = 0.0

    @api.depends('price_unit', 'split_method', 'cost_id', 'percentage')
    def _compute_cost_lines(self):
        super(LandedCostLine, self)._compute_cost_lines()

        for line in self.filtered(lambda l: l.split_method == 'construction_costs' and l.move_id):
            move = line.move_id
            if move and move.purchase_line_id:
                purchase_line = move.purchase_line_id
                product_price = purchase_line.price_unit
                if purchase_line.currency_id != purchase_line.company_id.currency_id:
                    product_price *= purchase_line.currency_id.rate
                
                cost_per_unit = float_round(
                    (line.percentage / 100) * product_price,
                    precision_digits=2
                )
                line.price_unit = cost_per_unit


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    def button_validate(self):
        res = super(StockLandedCost, self).button_validate()
        
        # تحديث تكلفة المنتج بعد تأكيد التكاليف
        for cost in self:
            for line in cost.cost_lines:
                if line.split_method == 'construction_costs' and line.product_id:
                    # حساب التكلفة الجديدة
                    new_cost = line.product_id.standard_price + line.price_unit
                    
                    # تحديث تكلفة المنتج
                    line.product_id.sudo().write({
                        'standard_price': new_cost
                    })
        
        return res
