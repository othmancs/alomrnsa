from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    customer_name = fields.Char(string="اسم العميل")
    customer_phone = fields.Char(string="رقم الهاتف")

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
        })
        return invoice_vals

    def _create_invoice_vals(self):
        self.ensure_one()
        invoice_vals = {
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone
        }
        return invoice_vals

    _rec_name = 'customer_name'

    def _search_customer_fields(self, operator, value):
        return ['|', ('customer_name', operator, value), ('customer_phone', operator, value)]
