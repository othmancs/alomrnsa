# models/purchase_order.py

from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    landed_cost_total = fields.Float(
        string='Landed Cost Total',
        compute='_compute_landed_cost_total',
        store=True
    )
    
    @api.depends('invoice_ids')
    def _compute_landed_cost_total(self):
        for order in self:
            total = 0.0
            if 'stock.landed.cost' in self.env:  # التحقق من وجود النموذج
                for invoice in order.invoice_ids:
                    landed_costs = self.env['stock.landed.cost'].search([
                        ('vendor_bill_id', '=', invoice.id)
                    ])
                    total += sum(landed_costs.mapped('amount_total'))
            order.landed_cost_total = total
