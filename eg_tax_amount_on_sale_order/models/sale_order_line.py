from odoo import api, fields, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"
    _description = "Sale Order Line"

    tax_amount = fields.Float(string="Tax Amount", compute="_compute_tax_amount")

    @api.onchange("product_uom_qty", "tax_id")
    def _compute_tax_amount(self):
        for sale_line_id in self:
            tax_only = 0
            for tax_id in sale_line_id.tax_id:
                tax_only += sale_line_id.price_unit * (tax_id.amount / 100)
            sale_line_id.tax_amount = tax_only * sale_line_id.product_uom_qty
