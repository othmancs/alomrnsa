from odoo import models, api

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_post(self):
        super().action_post()
        for payment in self:
            invoices = self.env['account.move'].search([
                ('partner_id', '=', payment.partner_id.id),
                ('state', '=', 'posted'),
                ('payment_state', '!=', 'paid'),
                ('move_type', '=', 'out_invoice')
            ], order='invoice_date asc')  # ترتيب حسب الأقدم

            remaining_amount = payment.amount
            for invoice in invoices:
                if remaining_amount <= 0:
                    break
                to_reconcile = min(invoice.amount_residual, remaining_amount)
                move_line = payment.move_id.line_ids.filtered(lambda l: l.account_internal_type == 'receivable')
                invoice_line = invoice.line_ids.filtered(lambda l: l.account_internal_type == 'receivable')
                (move_line + invoice_line).reconcile()
                remaining_amount -= to_reconcile
