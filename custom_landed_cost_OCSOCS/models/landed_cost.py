# -*- coding: utf-8 -*-
from odoo import models, fields, api

class LandedCost(models.Model):
    _inherit = 'stock.landed.cost'
    
    def _get_cost_distribution_methods(self):
        """ إضافة خيار تكاليف العمران إلى طرق التوزيع """
        methods = super(LandedCost, self)._get_cost_distribution_methods()
        methods.append(('urbanization', 'تكاليف العمران (حسب القيمة)'))
        return methods

class LandedCostLines(models.Model):
    _inherit = 'stock.landed.cost.lines'
    
    @api.depends('cost_id', 'split_method')
    def _compute_price_unit(self):
        """ تخصيص طريقة الحساب لخيار تكاليف العمران """
        super(LandedCostLines, self)._compute_price_unit()
        for line in self:
            if line.split_method == 'urbanization':
                if not line.cost_id:
                    line.price_unit = 0.0
                    continue
                
                total = 0.0
                for line_inv in line.cost_id.picking_ids.move_ids:
                    total += line_inv.product_id.standard_price * line_inv.product_qty
                
                if total == 0.0:
                    line.price_unit = 0.0
                else:
                    line.price_unit = line.price_unit / total