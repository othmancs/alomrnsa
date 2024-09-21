from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    customer_name = fields.Char(string="اسم العميل")
    customer_phone = fields.Char(string="رقم الهاتف")

    def _prepare_invoice(self):
        """إضافة الحقول الخاصة باسم العميل ورقم هاتفه عند إنشاء الفاتورة"""
        # استدعاء super للتأكد من الحصول على القيم الأصلية
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        
        # التحقق من وجود الحقول قبل تحديثها لتجنب التكرار
        if 'customer_name' not in invoice_vals:
            invoice_vals['customer_name'] = self.customer_name
        if 'customer_phone' not in invoice_vals:
            invoice_vals['customer_phone'] = self.customer_phone
        
        return invoice_vals

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
