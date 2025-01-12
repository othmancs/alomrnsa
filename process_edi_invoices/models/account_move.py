import re
from odoo import models

def clean_text(text):
    """إزالة المحارف غير القابلة للطباعة."""
    if text:
        return re.sub(r'[^\x20-\x7E]', '', text)
    return text

class AccountMove(models.Model):
    _inherit = 'account.move'

    def process_selected_invoices(self):
        """Execute `button_process_edi_web_services` for selected invoices."""
        for invoice in self:
            if hasattr(invoice, 'button_process_edi_web_services'):
                # تنظيف البيانات قبل المعالجة
                invoice_data = clean_text(invoice._l10n_sa_generate_unsigned_data())
                invoice.button_process_edi_web_services()

# from odoo import models

# class AccountMove(models.Model):
#     _inherit = 'account.move'

#     def process_selected_invoices(self):
#         """Execute `button_process_edi_web_services` for selected invoices."""
#         for invoice in self:
#             if hasattr(invoice, 'button_process_edi_web_services'):
#                 invoice.button_process_edi_web_services()
