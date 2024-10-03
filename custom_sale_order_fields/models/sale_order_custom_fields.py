from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    name_custom = fields.Char(string="اسم العميل")
    num_custom = fields.Char(string="رقم الجوال")

    # إعداد الفاتورة مع تمرير الحقول المخصصة
    @api.model
    def _prepare_invoice(self):
        # تأكد من أنك تستدعي super بشكل صحيح بدون self
        invoice_vals = super()._prepare_invoice()
        if self.name_custom and self.num_custom:
            invoice_vals.update({
                'name_custom': self.name_custom,
                'num_custom': self.num_custom,
            })
        return invoice_vals

class AccountMove(models.Model):
    _inherit = 'account.move'

    # إضافة الحقول في نموذج الفاتورة
    name_custom = fields.Char(string="اسم العميل")
    num_custom = fields.Char(string="رقم الجوال")
