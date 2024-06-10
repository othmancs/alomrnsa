from odoo import api, models, _, fields
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_post(self):
        result = super(AccountPayment, self).action_post()
        if self.env.user.has_group('sb_group_access.cannot_register_payment'):
            raise UserError(_("You are not authorized to register payment"))
        return result
