# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def _create_payments(self):
        """
            Override method for the generate warranty serial numebr and to get invoice_id
        """
        res = super(AccountPaymentRegister, self)._create_payments()
        for invoice in res.reconciled_invoice_ids:
            for invoice_line in invoice.invoice_line_ids:
                if invoice_line.sale_line_ids.mapped('warranty_details'):
                    for qty in range(int(round(invoice_line.quantity,0))):
                        for sale_line in invoice_line.sale_line_ids:
                            for warranty in sale_line.warranty_details.filtered(lambda l: l.state == 'pending' and not l.sale_invoice_id):
                                warranty.sale_invoice_id = invoice.id
                                break
                        for warranty in sale_line.warranty_details.filtered(lambda l: l.serial_id and l.sale_invoice_id and l.state == 'pending'):
                            warranty.action_running()
        return res
