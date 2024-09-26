from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    name_custom = fields.Char(string="اسم العميل")
    num_custom = fields.Integer(string="رقم العميل")
