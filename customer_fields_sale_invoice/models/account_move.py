from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    customer_name = fields.Char(string="Customer Name", readonly=True)
    customer_phone = fields.Char(string="Customer Phone", readonly=True)
class AccountMove(models.Model):
    _inherit = 'account.move'

    _rec_name = 'customer_name'

    def _search_customer_fields(self, operator, value):
        return ['|', ('customer_name', operator, value), ('customer_phone', operator, value)]
