from odoo import fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_method = fields.Selection([
        ('option1', 'نقدى'),
        ('option2', 'اجل'),
    ], string='طريقه الدفع', required=True)
    customer_name = fields.Char(string="اسم العميل")
    customer_phone = fields.Char(string="رقم هاتف العميل")

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()

        # إضافة طريقة الدفع و معرف المنشئ إلى invoice_vals
        invoice_vals['payment_method'] = self.payment_method
        invoice_vals['created_by_id'] = self.created_by_id.id
        
        return invoice_vals
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = ['|', ('customer_name', operator, name), ('customer_phone', operator, name)]
        return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)

    # تخصيص الاسم الذي يظهر في القائمة
    _rec_name = 'customer_name'
