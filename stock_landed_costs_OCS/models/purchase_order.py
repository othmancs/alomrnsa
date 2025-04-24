from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    company_currency_id = fields.Many2one(
        'res.currency',
        string="Company Currency",
        related='company_id.currency_id',
        readonly=True
    )

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
            company_currency = order.company_currency_id
            if order.currency_id != company_currency:
                amount_in_sar = order.currency_id._convert(
                    order.amount_total, company_currency, order.company_id, order.date_order or fields.Date.today())
                order.total_supplier_cost = amount_in_sar + order.landed_cost_total
            else:
                order.total_supplier_cost = order.amount_total + order.landed_cost_total
