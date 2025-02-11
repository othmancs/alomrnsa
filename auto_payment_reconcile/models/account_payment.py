from odoo import models, api

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_post(self):
        super().action_post()
        for payment in self:
            invoices = self.env['account.move'].search([
                ('partner_id', '=', payment.partner_id.id),
                ('state', '=', 'posted'),
                ('move_type', '=', 'out_invoice')
            ], order='invoice_date asc')  # ترتيب حسب الأقدم

            # تصفية الفواتير غير المسددة بعد البحث لتجنب مشاكل الحقول غير المخزنة
            invoices = invoices.filtered(lambda inv: inv.payment_state != 'paid')

            remaining_amount = payment.amount
            for invoice in invoices:
                if remaining_amount <= 0:
                    break
                to_reconcile = min(invoice.amount_residual, remaining_amount)
                
                # جلب الخطوط المحاسبية الصحيحة للمصالحة
                move_line = payment.move_id.line_ids.filtered(lambda l: l.account_id.account_type == 'asset_receivable')
                invoice_line = invoice.line_ids.filtered(lambda l: l.account_id.account_type == 'asset_receivable')
                
                (move_line + invoice_line).reconcile()
                remaining_amount -= to_reconcile
