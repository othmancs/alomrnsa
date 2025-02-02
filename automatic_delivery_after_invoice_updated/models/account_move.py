
from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super(AccountMove, self).action_post()

        for invoice in self:
            if invoice.move_type == 'out_invoice' and invoice.invoice_origin:
                sale_order = self.env['sale.order'].search([('name', '=', invoice.invoice_origin)], limit=1)
                if sale_order:
                    sale_order.action_confirm()

                    for picking in sale_order.picking_ids.filtered(lambda p: p.state in ['waiting', 'confirmed']):
                        picking.action_assign()
                        picking.button_validate()

        return res
