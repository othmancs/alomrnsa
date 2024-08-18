from odoo import fields, models, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    qty_on_hand = fields.Float(string='Quantity on Hand', compute='_compute_qty_on_hand')


    @api.depends('product_id')
    def _compute_qty_on_hand(self):
        for line in self:
            quant = self.env['stock.quant'].search([
                ('product_id', '=', line.product_id.id),
                ('location_id.usage', '=', 'internal')
            ])
            line.qty_on_hand = sum(quant.mapped('quantity'))

    @api.model
    def create(self, vals):
        line = super(PurchaseOrderLine, self).create(vals)
        line._compute_qty_on_hand()
        return line

    def write(self, vals):
        res = super(PurchaseOrderLine, self).write(vals)
        self._compute_qty_on_hand()
        return res


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    printed_by = fields.Char(string="طبع بواسطة", compute="_compute_printed_by")
    def _compute_printed_by(self):
        for record in self:
            record.printed_by = self.env.user.name