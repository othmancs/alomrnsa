from odoo import api, models, _, fields
from odoo.exceptions import UserError , ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    smart_field=fields.Char(string="الرقم المرجعى لبرناج سمارت")


    def action_post(self):
        for invoice in self:
            # Check if the required field is empty or has less than 4 digits
            if not invoice.smart_field:
                raise UserError(" الرقم المرجعى لبرناج سمارت اجبارى")
            if len(str(invoice.smart_field)) < 4:
                raise UserError("الرقم المرجعى لبرناج سمارت يجب ان يتكون من اربعه ارقام او اكثر")
                # Check if the field contains only zeros
            if str(invoice.smart_field).strip('0') == '':
                raise UserError("الرقم المرجعى لبرناج سمارت لا يمكن ان يكون اصفار فقط")
                # Check if the field starts with zero
            if str(invoice.smart_field).startswith('0'):
                raise UserError("الرقم المرجعى لبرناج سمارت لا يمكن ان يبدأ بصفر")
        # Call the original method to proceed with posting
        return super(AccountInvoice, self).action_post()

