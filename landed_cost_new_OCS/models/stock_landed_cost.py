from odoo import models, fields, api
from odoo.tools.float_utils import float_round

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
                    # حساب إجمالي تكلفة الشراء لجميع المنتجات
                    all_moves = pickings.mapped('move_lines')
                    purchase_lines = all_moves.mapped('purchase_line_id')
                    
                    if purchase_lines:
                        total_purchase_cost = sum(
                            pl.price_unit * pl.product_qty 
                            for pl in purchase_lines
                            if pl.price_unit and pl.product_qty
                        )
                        
                        if total_purchase_cost != 0:
                            percentage = total_cost / total_purchase_cost
                            
                            # الحصول على حركة المخزن المرتبطة بالخط الحالي
                            current_move = line.move_id
                            if current_move and current_move.purchase_line_id:
                                # سعر الشراء للصنف الحالي
                                product_price = current_move.purchase_line_id.price_unit
                                # كمية الصنف الحالي
                                product_qty = current_move.product_qty or 1
                                
                                # حساب التكلفة الجديدة مع التقريب إلى منزلتين عشريتين
                                line.price_unit = float_round(
                                    product_price * percentage,
                                    precision_digits=2
                                )
