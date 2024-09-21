from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    customer_name = fields.Char(string="Customer Name")
    customer_phone = fields.Char(string="Customer Phone")

    @api.model
    def create(self, vals):
        """عند إنشاء فاتورة، يتم تمرير اسم ورقم العميل تلقائيًا إلى الفاتورة."""
        res = super(SaleOrder, self).create(vals)
        if res:
            res._create_invoice_vals()
        return res

    def _create_invoice_vals(self):
        """تحديث الحقول في الفاتورة عند إنشائها"""
        self.ensure_one()
        invoice_vals = {
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone
        }
        return invoice_vals
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    _rec_name = 'customer_name'

    def _search_customer_fields(self, operator, value):
        return ['|', ('customer_name', operator, value), ('customer_phone', operator, value)]
