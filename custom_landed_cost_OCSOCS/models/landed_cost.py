# -*- coding: utf-8 -*-
from odoo import models, fields, api

class LandedCost(models.Model):
    _inherit = 'stock.landed.cost'
    
    def _get_cost_distribution_methods(self):
        """ إضافة خيار تكاليف العمران إلى طرق التوزيع """
        methods = super(LandedCost, self)._get_cost_distribution_methods()
        methods.append(('construction_costs', 'تكاليف العمران (حسب القيمة)'))
        return methods

    def _create_valuation_lines(self):
        """ تعديل الدالة لتجميع بنود المنتجات """
        lines = super(LandedCost, self)._create_valuation_lines()
        grouped_lines = {}
        
        # تجميع البنود حسب المنتج
        for line in lines:
            key = (line['product_id'], line['cost_line_id'])
            if key not in grouped_lines:
                grouped_lines[key] = line.copy()
            else:
                grouped_lines[key]['additional_landed_cost'] += line['additional_landed_cost']
                grouped_lines[key]['quantity'] += line['quantity']
        
        return list(grouped_lines.values())

class LandedCostLines(models.Model):
    _inherit = 'stock.landed.cost.lines'
    
    @api.depends('cost_id', 'split_method')
    def _compute_price_unit(self):
        """ تخصيص طريقة الحساب لخيار تكاليف العمران """
        super(LandedCostLines, self)._compute_price_unit()
        for line in self:
            if line.split_method == 'construction_costs':
                if not line.cost_id:
                    line.price_unit = 0.0
                    continue
                
                total = 0.0
                for line_inv in line.cost_id.picking_ids.move_ids:
                    total += line_inv.product_id.standard_price * line_inv.product_qty
                
                line.price_unit = line.price_unit / total if total else 0.0
