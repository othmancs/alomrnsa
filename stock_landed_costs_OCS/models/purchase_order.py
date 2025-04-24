# models/purchase_order.py
from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    landed_cost_total = fields.Float(
        string='صافي التكلفة',
        compute='_compute_landed_cost_total',
        store=True
    )
    
    total_supplier_cost = fields.Monetary(
        string="Total Supplier Cost",
        compute="_compute_total_supplier_cost",
        store=True,
        currency_field='currency_id'
    )
    total_in_sar = fields.Monetary(
    string="Total in SAR",
    compute='_compute_total_in_sar',
    currency_field='company_currency_id',
    readonly=True,
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
    @api.depends('amount_total', 'landed_cost_total', 'currency_id', 'total_in_sar')
    def _compute_total_supplier_cost(self):
        for order in self:
            if order.currency_id.name == 'USD':  # ✅ تم التعديل من 'US' إلى 'USD'
                order.total_supplier_cost = order.total_in_sar + order.landed_cost_total
            else:
                order.total_supplier_cost = order.amount_total + order.landed_cost_total
    # @api.depends('amount_total', 'landed_cost_total')
    # def _compute_total_supplier_cost(self):
    #     for order in self:
    #         order.total_supplier_cost = order. + order.landed_cost_total
