import re
import logging
from odoo import models

_logger = logging.getLogger(__name__)

def clean_text(text):
    """إزالة المحارف غير القابلة للطباعة والتأكد من صحة النص."""
    if not text:
        return ""  # إرجاع نص فارغ بدلًا من None
    # إذا كان النص من نوع bytes نقوم بفك الترميز إلى utf-8
    if isinstance(text, bytes):
        try:
            text = text.decode("utf-8")
        except Exception as e:
            _logger.error("Error decoding text: %s", e)
            raise ValueError("Failed to decode text: {}".format(e))
    return re.sub(r'[^\x20-\x7E]', '', text)

class AccountMove(models.Model):
    _inherit = 'account.move'

    def process_selected_invoices(self):
        """تنفيذ عملية EDI للفواتير المحددة."""
        for invoice in self:
            if hasattr(invoice, 'button_process_edi_web_services'):
                # الحصول على بيانات التوقيع غير الموقعة
                invoice_data = invoice._l10n_sa_generate_unsigned_data()
                _logger.info("Invoice data before cleaning: %s", invoice_data)
                
                # تنظيف البيانات للتأكد من أنها نصية وخالية من المحارف غير القابلة للطباعة
                invoice_data = clean_text(invoice_data)
                _logger.info("Invoice data after cleaning: %s", invoice_data)
                
                # التحقق من أن البيانات ليست فارغة أو من نوع غير نصي
                if not invoice_data:
                    raise ValueError("No valid invoice data found for invoice ID: %s" % invoice.id)
                if not isinstance(invoice_data, str):
                    raise ValueError("Invoice data must be a string, got %s instead" % type(invoice_data))
                
                # تنفيذ العملية الخاصة بمعالجة الفاتورة الإلكترونية
                invoice.button_process_edi_web_services()

# import re
# from odoo import models

# def clean_text(text):
#     """إزالة المحارف غير القابلة للطباعة."""
#     if text:
#         return re.sub(r'[^\x20-\x7E]', '', text)
#     return text

# class AccountMove(models.Model):
#     _inherit = 'account.move'

#     def process_selected_invoices(self):
#         """Execute `button_process_edi_web_services` for selected invoices."""
#         for invoice in self:
#             if hasattr(invoice, 'button_process_edi_web_services'):
#                 # تنظيف البيانات قبل المعالجة
#                 invoice_data = clean_text(invoice._l10n_sa_generate_unsigned_data())
#                 invoice.button_process_edi_web_services()

