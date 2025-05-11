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
                total_costs = line.cost_id.amount_total  # إجمالي التكاليف (18,613.83 في المثال)
                pickings = line.cost_id.picking_ids
                
                if pickings:
                    # حساب إجمالي تكلفة الشراء لجميع المنتجات (82,761.57 في المثال)
                    all_moves = pickings.mapped('move_lines')
                    purchase_lines = all_moves.mapped('purchase_line_id')
                    
                    if purchase_lines:
                        total_purchase_cost = sum(
                            pl.price_unit * pl.product_qty * (pl.currency_id.rate if pl.currency_id != pl.company_id.currency_id else 1)
                            for pl in purchase_lines
                            if pl.price_unit and pl.product_qty
                        )
                        
                        if total_purchase_cost != 0:
                            # حساب النسبة المئوية (22% في المثال)
                            percentage = total_costs / total_purchase_cost
                            
                            # الحصول على حركة المخزن المرتبطة بالخط الحالي
                            current_move = line.move_id
                            if current_move and current_move.purchase_line_id:
                                purchase_line = current_move.purchase_line_id
                                
                                # تحويل سعر الشراء للعملة الأساسية إذا كان مختلفاً
                                product_price = purchase_line.price_unit
                                if purchase_line.currency_id != purchase_line.company_id.currency_id:
                                    product_price = purchase_line.price_unit * purchase_line.currency_id.rate
                                
                                # كمية الصنف الحالي
                                product_qty = current_move.product_qty or 1
                                
                                # حساب التكلفة الجديدة (النسبة × سعر الوحدة بعد التحويل)
                                cost_per_unit = float_round(
                                    (percentage * product_price),
                                    precision_digits=2
                                )
                                
                                line.price_unit = cost_per_unit
