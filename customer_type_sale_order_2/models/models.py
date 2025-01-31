from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    payment_type = fields.Selection([
        ('cash', 'كاش'),
        ('credit', 'آجل')
    ], string='Payment Type', default='cash')

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    payment_type = fields.Selection([
            ('cash', 'كاش'),
            ('credit', 'آجل')
        ], string='Payment Type', related='partner_id.payment_type', store=True)

    def _create_delivery_order(self):
        for order in self:
            if order.partner_id.payment_type == 'cash' and not order.invoice_ids.filtered(lambda inv: inv.state == 'paid'):
                raise ValidationError("Payment must be registered before creating the delivery order for cash customers.")
            return super(SaleOrder, order)._create_delivery_order()
 
class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, values):
        move = super(AccountMove, self).create(values)
        if move.partner_id.payment_type == 'cash' and move.state == 'posted' and not move.payment_state == 'paid':
            raise ValidationError("Payment must be registered for cash customers before proceeding.")
        return move
