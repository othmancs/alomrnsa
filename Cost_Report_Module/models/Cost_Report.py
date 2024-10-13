from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    additional_cost = fields.Float(string='Additional Cost', default=0.0)

    @api.depends('price_unit', 'product_qty', 'additional_cost')
    def _compute_total_cost(self):
        for line in self:
            line.total_cost = (line.price_unit * line.product_qty) + line.additional_cost

    total_cost = fields.Float(string='Total Cost', compute='_compute_total_cost', store=True)
