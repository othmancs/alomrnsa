from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    customer_name = fields.Char(string='اسم العميل')
    customer_phone = fields.Char(string='رقم الجوال')

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
        })
        return invoice_vals
