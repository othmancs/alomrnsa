from odoo import models, fields, api

class LandedCostLine(models.Model):
    _inherit = 'stock.landed.cost.lines'
    
    split_method = fields.Selection(
        selection_add=[('construction_costs', 'تكاليف العمران')],
        ondelete={'construction_costs': 'set default'},
        default='by_quantity'
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
                        # حساب إجمالي تكلفة الشراء لكل المنتجات
                        total_purchase_cost = sum(purchase_lines.mapped(lambda pl: pl.price_unit * pl.product_qty))
                        
                        if total_purchase_cost != 0:
                            # حساب النسبة المئوية
                            percentage = total_cost / total_purchase_cost
                            
                            # الحصول على سعر شراء المنتج الحالي
                            current_move = line.move_id
                            if current_move and current_move.purchase_line_id:
                                product_purchase_price = current_move.purchase_line_id.price_unit
                                # حساب التكلفة الجديدة
                                line.price_unit = product_purchase_price * percentage
