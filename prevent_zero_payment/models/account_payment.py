from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.constrains('amount')
    def _check_payment_amount(self):
        for payment in self:
            if payment.amount == 0:
                raise ValidationError("لا يمكنك إنشاء دفعة بقيمة صفر!")
