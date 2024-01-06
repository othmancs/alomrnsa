from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        for rec in self:
            if rec.move_type == 'out_refund':
                for line in rec.invoice_line_ids:
                    for rev_line in rec.reversed_entry_id.invoice_line_ids:
                        if line.product_id.id == rev_line.product_id.id:
                            if line.quantity > rev_line.quantity:
                                raise ValidationError(_("The returned amount is more than purchased amount"))

        result = super(AccountMove, self).action_post()
        return result
