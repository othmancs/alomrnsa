from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    purchase_order_number = fields.Char(string='رقم أمر الشراء', copy=True)

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        invoice_vals['purchase_order_number'] = self.purchase_order_number
        return invoice_vals
