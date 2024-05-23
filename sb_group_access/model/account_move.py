from odoo import api, models, _
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        result = super(AccountInvoice, self).action_post()
        if self.env.user.has_group('sb_group_access.cannot_creat_invoice'):
            raise UserError(_("You are not authorized to creat invoice"))
        return result

    def creat(self,vals):
        result = super(AccountInvoice, self).creat(vals)
        if self.env.user.has_group('sb_group_access.cannot_creat_invoice'):
            raise UserError(_("You are not authorized to creat invoice"))
        return result

    def write(self,vals):
        result = super(AccountInvoice, self).write(vals)
        if self.env.user.has_group('sb_group_access.cannot_creat_invoice'):
            raise UserError(_("You are not authorized to creat invoice"))
        return result
