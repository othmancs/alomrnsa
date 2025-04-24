# models/purchase_order.py
from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    landed_cost_total = fields.Float(
        string='صافي التكلفة',
        compute='_compute_landed_cost_total',
        store=True
    )
    
    total_supplier_cost = fields.Float(
        string='إجمالي المورد',
        compute='_compute_total_supplier_cost',
        store=True
    )
    
    @api.depends('invoice_ids')
    def _compute_landed_cost_total(self):
        for order in self:
            total = 0.0
            if 'stock.landed.cost' in self.env:
                for invoice in order.invoice_ids:
                    landed_costs = self.env['stock.landed.cost'].search([
                        ('vendor_bill_id', '=', invoice.id)
                    ])
                    total += sum(landed_costs.mapped('amount_total'))
            order.landed_cost_total = total
    @api.depends('amount_total', 'landed_cost_total', 'currency_id')
    def _compute_total_supplier_cost(self):
        for order in self:
            if order.currency_id.name == 'US':
                # إذا كانت العملة دولار أمريكي، نجمع landed_cost_total مع total_in_sar
                order.total_supplier_cost = order.total_in_sar+ order.landed_cost_total
            elif order.currency_id.name == 'SAR':
    
               order.total_supplier_cost = order.amount_total + order.landed_cost_total        
            else:
                # حالة افتراضية إذا كانت العملة غير المذكورة
                order.total_supplier_cost = order.landed_cost_total
    # @api.depends('amount_total', 'landed_cost_total')
    # def _compute_total_supplier_cost(self):
    #     for order in self:
    #         order.total_supplier_cost = order. + order.landed_cost_total
