from odoo import fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    name_custom  = fields.Char(string="اسم العميل")
    num_custom  = fields.Char(string="رقم الجوال")

#  @api.model
#     def _prepare_invoice(self):
#         invoice_vals = super(SaleOrder, self)._prepare_invoice()
#         invoice_vals.update({
#             'name_custom': self.name_custom,
#             'num_custom': self.num_custom,
#         })
#         return invoice_vals
        
# class AccountMove(models.Model):
#     _inherit = 'account.move'

#     # إضافة الحقول المخصصة للفواتير
#     name_custom = fields.Char(string="اسم العميل", related='sale_order_id.name_custom')
#     num_custom = fields.Char(string="رقم الجوال", related='sale_order_id.num_custom')
