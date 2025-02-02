from odoo import fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_method = fields.Selection([
        ('option1', 'نقدى'),
        ('option2', 'اجل'),
    ], string='طريقه الدفع', required=False)
    # payment_type = fields.Selection([
    #     ('cash', 'Cash'),
    #     ('credit', 'Credit')
    # ], string='Payment Type')
 

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['payment_type'] = self.payment_type
        # إضافة طريقة الدفع و معرف المنشئ إلى invoice_vals
        invoice_vals['payment_method'] = self.payment_method
        invoice_vals['created_by_id'] = self.created_by_id.id
        
        return invoice_vals

