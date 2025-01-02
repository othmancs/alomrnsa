
from odoo import models

class AccountMove(models.Model):
    _inherit = 'account.move'

    def process_selected_invoices(self):
        """Execute `button_process_edi_web_services` for selected invoices."""
        for invoice in self:
            if hasattr(invoice, 'button_process_edi_web_services'):
                invoice.button_process_edi_web_services()
