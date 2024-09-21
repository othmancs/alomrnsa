from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_method = fields.Selection([
        ('option1', 'نقدى'),
        ('option2', 'اجل'),
    ], string='طريقه الدفع', required=True)

class SaleOrderEditReports(models.Model):
    _inherit = 'sale.order'

    customer_name = fields.Char(string="اسم العميل")
    customer_phone = fields.Char(string="رقم الهاتف")

    def _prepare_invoice(self):
        # استدعاء الدالة من الكلاس المباشر
        invoice_vals = super(SaleOrderEditReports, self)._prepare_invoice()
        
        # إضافة الحقول الخاصة بك إلى invoice_vals
        invoice_vals.update({
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
        })
        
        return invoice_vals
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['payment_method'] = self.payment_method
        invoice_vals['created_by_id'] = self.created_by_id.id
        return invoice_vals




