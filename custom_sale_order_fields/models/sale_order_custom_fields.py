from odoo import fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    name_custom  = fields.Char(string="اسم العميل")
    num_custom  = fields.Char(string="رقم الجوال")