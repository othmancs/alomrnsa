from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    purchase_order_number = fields.Char(string='رقم أمر الشراء', related='invoice_origin', readonly=True)
