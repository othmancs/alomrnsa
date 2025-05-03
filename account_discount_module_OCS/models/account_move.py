from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    allowed_discount = fields.Float(
        string='الخصم المسموح به',
        digits='Product Price',
        help='خصم لا يتجاوز 1 ريال للكسور العشرية',
        default=0.0
    )
    
    @api.constrains('allowed_discount')
    def _check_allowed_discount(self):
        for move in self:
            if move.move_type == 'out_invoice' and (move.allowed_discount < 0 or move.allowed_discount > 1):
                raise ValidationError(_('الخصم المسموح به يجب أن يكون بين 0 و 1 ريال فقط!'))
    
    @api.depends('invoice_line_ids', 'allowed_discount', 'tax_totals')
    def _compute_amount(self):
        super()._compute_amount()
        for move in self:
            if move.move_type == 'out_invoice' and move.allowed_discount:
                discount_amount = min(move.allowed_discount, 1)
                # تحديث الإجماليات
                move.amount_total = move.amount_total - discount_amount
                if move.tax_totals:
                    move.tax_totals = {
                        **move.tax_totals,
                        'amount_total': move.tax_totals['amount_total'] - discount_amount,
                        'formatted_amount_total': move.currency_id.format(move.tax_totals['amount_total'] - discount_amount)
                    }
    
    def _recompute_tax_lines(self, recompute_tax_base_amount=False):
        res = super()._recompute_tax_lines(recompute_tax_base_amount)
        self._compute_amount()
        return res
