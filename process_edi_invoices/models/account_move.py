# # -*- coding: utf-8 -*-
# import re
# import logging
# from odoo import models, api
# from lxml import etree

# _logger = logging.getLogger(__name__)

# def clean_text(text):
#     """إزالة المحارف غير القابلة للطباعة والتأكد من صحة النص."""
#     if not text:
#         return ""  # إرجاع نص فارغ بدلًا من None
#     # إذا كان النص من نوع bytes، نقوم بفك الترميز إلى utf-8
#     if isinstance(text, bytes):
#         try:
#             text = text.decode("utf-8")
#             _logger.info("تم فك ترميز النص من bytes إلى string")
#         except Exception as e:
#             _logger.error("خطأ أثناء فك ترميز النص: %s", e)
#             raise ValueError("فشل فك ترميز النص: {}".format(e))
#     # إزالة المحارف غير القابلة للطباعة
#     return re.sub(r'[^\x20-\x7E]', '', text)

# class AccountMove(models.Model):
#     _inherit = 'account.move'

#     def _l10n_sa_generate_unsigned_data(self):
#         """
#         تجاوز دالة توليد بيانات XML غير الموقعة للتأكد من أن البيانات نصية وليس من نوع bytes.
#         """
#         # استدعاء الدالة الأصلية للحصول على بيانات XML
#         xml_data = super(AccountMove, self)._l10n_sa_generate_unsigned_data()
#         _logger.info("نوع البيانات الأصلية لـ XML: %s", type(xml_data))
#         # إذا كانت البيانات من نوع bytes، نقوم بفك الترميز إلى string
#         if isinstance(xml_data, bytes):
#             try:
#                 xml_data = xml_data.decode("utf-8")
#                 _logger.info("تم فك ترميز xml_data من bytes إلى string")
#             except Exception as e:
#                 _logger.error("خطأ أثناء فك ترميز xml_data: %s", e)
#                 raise ValueError("فشل فك ترميز xml_data: {}".format(e))
#         return xml_data

#     def process_selected_invoices(self):
#         """تنفيذ عملية EDI للفواتير المحددة."""
#         for invoice in self:
#             if hasattr(invoice, 'button_process_edi_web_services'):
#                 # الحصول على بيانات XML غير الموقعة
#                 invoice_data = invoice._l10n_sa_generate_unsigned_data()
#                 _logger.info("بيانات الفاتورة قبل التنظيف: %s", invoice_data)
                
#                 # تنظيف البيانات للتأكد من أنها نصية وخالية من المحارف غير القابلة للطباعة
#                 invoice_data = clean_text(invoice_data)
#                 _logger.info("بيانات الفاتورة بعد التنظيف: %s", invoice_data)
                
#                 # التحقق من أن البيانات ليست فارغة أو من نوع غير نصي
#                 if not invoice_data:
#                     raise ValueError("لم يتم العثور على بيانات فاتورة صالحة للفاتورة رقم: %s" % invoice.id)
#                 if not isinstance(invoice_data, str):
#                     raise ValueError("يجب أن تكون بيانات الفاتورة نصاً، لكن تم الحصول على: %s" % type(invoice_data))
                
#                 # تنفيذ العملية الخاصة بمعالجة الفاتورة الإلكترونية
#                 invoice.button_process_edi_web_services()

# # محاولة تجاوز دالة _l10n_sa_generate_invoice_xml_sha إذا كان نموذج account.edi.xml.ubl_21.zatca موجودًا
# try:
#     class AccountEdiXmlUbl21Zatca(models.AbstractModel):
#         _inherit = 'account.edi.xml.ubl_21.zatca'

#         def _l10n_sa_generate_invoice_xml_sha(self, xml_content):
#             """
#             تجاوز دالة توليد تجزئة XML للتأكد من أن xml_content من نوع string.
#             """
#             # التحقق من نوع xml_content وتحويله إلى string إن لزم الأمر
#             if isinstance(xml_content, bytes):
#                 try:
#                     xml_content = xml_content.decode("utf-8")
#                     _logger.info("تم فك ترميز xml_content من bytes إلى string")
#                 except Exception as e:
#                     _logger.error("خطأ أثناء فك ترميز xml_content: %s", e)
#                     raise ValueError("فشل فك ترميز xml_content: {}".format(e))
#             # محاولة تحليل محتوى XML للتأكد من صحته
#             try:
#                 root = etree.fromstring(xml_content)
#                 _logger.info("تم تحليل محتوى XML بنجاح")
#             except Exception as e:
#                 _logger.error("خطأ أثناء تحليل XML content: %s", e)
#                 raise ValueError("خطأ أثناء تحليل XML content: {}".format(e))
#             # متابعة تنفيذ الدالة الأصلية بعد التحقق من صحة xml_content
#             return super(AccountEdiXmlUbl21Zatca, self)._l10n_sa_generate_invoice_xml_sha(xml_content)
# except Exception as e:
#     _logger.info("نموذج account.edi.xml.ubl_21.zatca غير موجود في النظام أو حدث خطأ أثناء التحميل: %s", e)



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

