from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_balance = fields.Monetary(
        string='Customer Balance',
        compute='_compute_partner_balance',
        compute_sudo=True,  # Added for Odoo 17
        currency_field='currency_id',
        help='Current balance from partner ledger'
    )

    @api.depends('partner_id', 'partner_id.credit', 'partner_id.debit')
    def _compute_partner_balance(self):
        """Compute the current balance from the partner ledger."""
        for order in self:
            if not order.partner_id:
                order.partner_balance = 0.0
                continue

            # Get partner ledger balance
            # In partner ledger: credit is positive (amount we owe them)
            # debit is negative (amount they owe us)
            balance = order.partner_id.credit - order.partner_id.debit
            order.partner_balance = balance