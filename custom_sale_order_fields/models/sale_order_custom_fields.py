from odoo import fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    name_custom  = fields.Char(string="اسم العميل")
    num_custom  = fields.Char(string="رقم الجوال")
class AccountMove(models.Model):
    _inherit = 'account.move'

    # إضافة الحقول المخصصة للفواتير
    sale_order_id = fields.Many2one('sale.order', string='طلب البيع الأصلي')
    name_custom = fields.Char(string="اسم العميل", related='sale_order_id.name_custom')
    num_custom = fields.Char(string="رقم الجوال", related='sale_order_id.num_custom')
