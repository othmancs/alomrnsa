# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        """
            Override method for the add invoice id in warranty if paid invoice.
        """
        res = super(AccountMove, self).action_post()
        for rec in self:
            for invoice_line in rec.invoice_line_ids:
                if invoice_line.sale_line_ids.mapped('warranty_details') and rec.payment_state == 'paid':
                    for sale_line in invoice_line.sale_line_ids:
                        for warranty in sale_line.warranty_details.filtered(lambda l: l.state == 'pending' and not l.sale_invoice_id):
                            warranty.sale_invoice_id = rec.id
                            break
                    for warranty in sale_line.warranty_details.filtered(lambda l: l.serial_id and l.sale_invoice_id and l.state == 'pending'):
                        warranty.action_running()
        return res
