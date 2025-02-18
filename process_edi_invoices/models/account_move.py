import re
from odoo import models, fields
from lxml import etree


# import re
# from odoo import models

# def clean_text(text):
#     """إزالة المحارف غير القابلة للطباعة."""
#     if text:
#         return re.sub(r'[^\x20-\x7E]', '', text)
#     return text
def clean_text(text):
    """إزالة المحارف غير القابلة للطباعة من النصوص."""
    if text:
        return re.sub(r'[^\x20-\x7E\u0600-\u06FF]', '', text)  # يدعم العربية والإنجليزية فقط
    return text
# class AccountMove(models.Model):
#     _inherit = 'account.move'

#     def process_selected_invoices(self):
#         """Execute `button_process_edi_web_services` for selected invoices."""
#         for invoice in self:
#             if hasattr(invoice, 'button_process_edi_web_services'):
#                 # تنظيف البيانات قبل المعالجة
#                 invoice_data = clean_text(invoice._l10n_sa_generate_unsigned_data())
#                 invoice.button_process_edi_web_services()

class AccountMove(models.Model):
    _inherit = 'account.move'

    def process_selected_invoices(self):
        """تنظيف ومعالجة الفواتير المحددة."""
        for invoice in self:
            if hasattr(invoice, 'button_process_edi_web_services'):
                # تنظيف بيانات XML قبل المعالجة
                if hasattr(invoice, '_l10n_sa_generate_unsigned_data'):
                    raw_data = invoice._l10n_sa_generate_unsigned_data()
                    invoice_data = clean_text(raw_data)
                    invoice._l10n_sa_generate_unsigned_data = lambda: invoice_data  # استبدال الدالة مؤقتًا
                
                invoice.button_process_edi_web_services()
class AccountJournal(models.Model):
    _inherit = 'account.journal'

    def _l10n_sa_api_clearance(self, invoice, xml_content, PCSID_data):
        """تنظيف وتحليل XML قبل معالجته."""
        xml_content = clean_text(xml_content)  # تنظيف XML من المحارف غير الصالحة
        try:
            invoice_tree = etree.fromstring(xml_content.encode('utf-8'))
        except etree.XMLSyntaxError as e:
            raise ValueError(f"خطأ في تحليل XML: {e}")
        return invoice_tree
