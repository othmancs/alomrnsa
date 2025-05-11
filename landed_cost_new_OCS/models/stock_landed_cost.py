from odoo import models, fields, api
from odoo.tools.float_utils import float_round
from collections import defaultdict

class LandedCostLine(models.Model):
    _inherit = 'stock.landed.cost.lines'
    
    percentage = fields.Float(string="النسبة المئوية", compute='_compute_percentage', store=True, digits=(16, 2))
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
                    # استخدام move_ids بدلاً من move_lines للإصدارات الحديثة من أودو
                    all_moves = pickings.move_ids
                    purchase_lines = all_moves.purchase_line_id
                    
                    if purchase_lines:
                        total_purchase_cost = sum(
                            pl.price_unit * pl.product_qty * (pl.currency_id.rate if pl.currency_id != pl.company_id.currency_id else 1)
                            for pl in purchase_lines
                            if pl.price_unit and pl.product_qty
                        )
                        
                        line.percentage = (total_costs / total_purchase_cost) * 100 if total_purchase_cost != 0 else 0.0
                    else:
                        line.percentage = 0.0
                else:
                    line.percentage = 0.0
            else:
                line.percentage = 0.0
    
    @api.depends('price_unit', 'split_method', 'cost_id', 'percentage')
    def _compute_cost_lines(self):
        super(LandedCostLine, self)._compute_cost_lines()
        
        # تجميع البنود لكل منتج
        lines_to_process = self.filtered(lambda l: l.split_method == 'construction_costs' and l.move_id)
        product_lines = defaultdict(list)
        
        for line in lines_to_process:
            product_lines[line.move_id.id].append(line)
        
        # معالجة البنود المجمعة
        for move_id, lines in product_lines.items():
            if lines:
                main_line = lines[0]
                move = main_line.move_id
                
                if move and move.purchase_line_id:
                    purchase_line = move.purchase_line_id
                    product_price = purchase_line.price_unit
                    
                    if purchase_line.currency_id != purchase_line.company_id.currency_id:
                        product_price = purchase_line.price_unit * purchase_line.currency_id.rate
                    
                    # حساب التكلفة لكل وحدة
                    cost_per_unit = float_round(
                        (main_line.percentage / 100) * product_price,
                        precision_digits=2
                    )
                    
                    # تحديث البند الرئيسي
                    main_line.price_unit = cost_per_unit
                    
                    # حذف البنود الإضافية إن وجدت
                    if len(lines) > 1:
                        for extra_line in lines[1:]:
                            extra_line.unlink()
