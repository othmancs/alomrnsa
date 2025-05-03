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
    
    def _recompute_dynamic_lines(self, recompute_all_taxes=False, recompute_tax_base_amount=False):
        res = super(AccountMove, self)._recompute_dynamic_lines(
            recompute_all_taxes=recompute_all_taxes,
            recompute_tax_base_amount=recompute_tax_base_amount
        )
        
        for move in self:
            if move.move_type == 'out_invoice' and move.allowed_discount:
                discount_amount = min(move.allowed_discount, 1)
                move.amount_total = move.amount_untaxed + move.amount_tax - discount_amount
                
                if hasattr(move, 'tax_totals') and move.tax_totals:
                    move.tax_totals['amount_total'] = move.amount_total
                    move.tax_totals['formatted_amount_total'] = move.currency_id.format(move.amount_total)
        return res
    
    @api.onchange('allowed_discount')
    def _onchange_allowed_discount(self):
        if self.move_type == 'out_invoice':
            self._recompute_dynamic_lines()
