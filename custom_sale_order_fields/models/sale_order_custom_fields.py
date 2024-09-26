from odoo import fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    customer_name = fields.Char(string="اسم العميل")
    customer_phone = fields.Char(string="رقم الجوال")
