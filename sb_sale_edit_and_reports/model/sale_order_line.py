from odoo import fields, models



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice_line(self, **optional_values):
        invoice_vals = super(SaleOrderLine, self)._prepare_invoice_line()
        invoice_vals['purchase_price'] = self.purchase_price
        return invoice_vals
