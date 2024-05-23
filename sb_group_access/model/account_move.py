from odoo import api, models, _
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        result = super(AccountInvoice, self).create()
        if self.env.user.has_group('sb_group_access.cannot_creat_invoice'):
            raise UserError(_("You are not authorized to creat invoice"))
        return result
