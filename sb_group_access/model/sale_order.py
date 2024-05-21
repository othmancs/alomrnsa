from odoo import models, _
from odoo.exceptions import UserError


class SaleAccessButtons(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        if self.env.user.has_group('sb_group_access.cannot_confirm_sale_orders'):
            raise UserError(_("You are not authorized to confirm sales orders."))
        return super(SaleAccessButtons, self).action_confirm()

    def action_cancel(self):
        if self.env.user.has_group("sb_group_access.cannot_cancel_sale_orders"):
            raise UserError(_("You are not authorized to cancel sales orders."))
        return super(SaleAccessButtons, self).action_cancel()

    def _create_invoices(self, grouped=False, final=False, date=None):
        if self.env.user.has_group("sb_group_access.cannot_creat_invoice"):
            raise UserError(_("You are not authorized to creat invoices."))
        return super(SaleAccessButtons, self)._create_invoices()
