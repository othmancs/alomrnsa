from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        for rec in self:
            if rec.partner_id.sales_credit_limit > 0:

                customer_due_amount = sum(self.env['account.move'].search([
                    ('move_type', '=', 'out_invoice'),
                    ('partner_id', '=', rec.partner_id.id),
                    ('state', '=', 'posted')
                ]).mapped('amount_residual'))

                sale_without_invoice = self.env['sale.order'].search([
                    ('partner_id', '=', rec.partner_id.id),
                    ('invoice_ids', '=', False),
                    ('state', 'in', ['sale', 'done'])
                ])
                if sale_without_invoice:
                    order_amount = sum(sale_without_invoice.mapped('amount_total'))
                    allowed_amount = rec.partner_id.sales_credit_limit - customer_due_amount - order_amount
                    customer_due_amount += order_amount
                else:
                    allowed_amount = rec.partner_id.sales_credit_limit - customer_due_amount

                sale_with_invoice_draft = self.env['account.move'].search([
                    ('move_type', '=', 'out_invoice'),
                    ('partner_id', '=', rec.partner_id.id),
                    ('state', '=', 'draft'),
                    ('line_ids.sale_line_ids.order_id', '!=', False)
                ])
                if sale_with_invoice_draft:
                    draft_order_amount = sum(sale_with_invoice_draft.mapped('amount_total'))
                    allowed_amount = rec.partner_id.sales_credit_limit - customer_due_amount - draft_order_amount
                    customer_due_amount += draft_order_amount
                else:
                    allowed_amount = rec.partner_id.sales_credit_limit - customer_due_amount

                if allowed_amount < 0:
                    raise ValidationError(_(
                        "Customer Exceeded Sales Credit Limit = %s, Customer Due Amount = %s",
                        rec.partner_id.sales_credit_limit, customer_due_amount))
                if allowed_amount < rec.amount_total:
                    raise ValidationError(_('Customer Allowed Amount: %s \n ', allowed_amount))

        res = super(AccountMove, self).action_post()

        return res

    # def action_post(self):
    #     for rec in self:
    #         if rec.partner_id.sales_credit_limit > 0:
    #             customer_due_amount = sum(self.env['account.move'].search([
    #                 ('move_type', '=', 'out_invoice'),
    #                 ('payment_state', '!=', 'paid'),
    #                 ('partner_id', '=', rec.partner_id.id),
    #                 ('state', '=', 'posted')
    #             ]).mapped('amount_residual'))
    #             allowed_amount = rec.partner_id.sales_credit_limit - customer_due_amount
    #             if allowed_amount < 0:
    #                 raise ValidationError(_(
    #                     "Customer Exceeded his sales credit limit Sales Credit Limit = %s, Customer Due Amount = %s",
    #                     rec.partner_id.sales_credit_limit, customer_due_amount))
    #             if allowed_amount < rec.amount_total:
    #                 raise ValidationError(_('Customer Allowed amount is %s', allowed_amount))
    #
    #     res = super(AccountMove, self).action_post()
    #
    #     return res
