from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    tax_amount = fields.Float(
        string="Tax Amount", 
        compute="_compute_tax_amount", 
        store=True
    )

    @api.depends('tax_id', 'price_unit', 'product_uom_qty')
    def _compute_tax_amount(self):
        for line in self:
            if line.tax_id:
                taxes = line.tax_id.compute_all(
                    line.price_unit, 
                    line.order_id.currency_id, 
                    line.product_uom_qty, 
                    product=line.product_id, 
                    partner=line.order_id.partner_id
                )
                line.tax_amount = sum(t['amount'] for t in taxes['taxes'])
            else:
                line.tax_amount = 0.0


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            customer_taxes = self.partner_id.property_account_position_id.tax_ids
            for line in self.order_line:
                if customer_taxes:
                    line.tax_id = customer_taxes
                elif not line.tax_id:
                    line.tax_id = self.env['account.tax'].search([
                        ('type_tax_use', '=', 'sale'),
                        ('company_id', '=', self.company_id.id),
                        ('name', '=', 'Default Tax')
                    ], limit=1)
