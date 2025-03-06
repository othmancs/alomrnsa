from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    purchase_order_number = fields.Char(string='رقم أمر الشراء', copy=True)

    @api.onchange('state')
    def _onchange_state(self):
        if self.state != 'draft':
            self.purchase_order_number = self.purchase_order_number  # تثبيت القيمة عند التغيير
