from odoo import fields, models, api


class MaterialRequestLine(models.Model):
    _inherit = 'material.request.line'

    qty_available = fields.Integer(string='الكمية المتاحة', compute='_compute_qty_available')

    @api.depends('request_id.location_id')
    def _compute_qty_available(self):
        for rec in self:
            avail_qty = self.env['stock.quant'].search([
                '|',
                ('location_id', '=', rec.request_id.dest_location_id.id),
                ('parent_location_id', '=', rec.request_id.dest_location_id.id),
                ('product_id', '=', rec.product_id.id)
            ])

            if avail_qty:
                rec.qty_available = sum(avail_qty.mapped('quantity'))
            else:
                rec.qty_available = 0
