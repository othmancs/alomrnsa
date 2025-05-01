from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    allowed_discount = fields.Float(
        string='الخصم المسموح به',
        digits='Product Price',
        help='خصم لا يتجاوز 1 ريال للكسور العشرية'
    )
    
    @api.constrains('allowed_discount')
    def _check_allowed_discount(self):
        for move in self:
            if move.allowed_discount < 0 or move.allowed_discount > 1:
                raise ValidationError(_('الخصم المسموح به يجب أن يكون بين 0 و 1 ريال فقط!'))
    
    def _recompute_tax_lines(self, recompute_tax_base_amount=False):
        res = super(AccountMove, self)._recompute_tax_lines(recompute_tax_base_amount)
        for move in self:
            if move.allowed_discount:
                total_without_discount = sum(line.price_subtotal for line in move.invoice_line_ids)
                discount_amount = min(move.allowed_discount, 1)  # التأكد من عدم تجاوز 1 ريال
                move.amount_total = total_without_discount - discount_amount
        return res