from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        for picking in self:
            if picking.sale_id:  # إذا كان هناك أمر بيع مرتبط
                payment_type = picking.sale_id.payment_type  # جلب نوع الدفع من أمر البيع
                
                # التحقق من وجود فواتير مرتبطة بأمر البيع
                if not picking.sale_id.invoice_ids:
                    raise UserError(_(
                        "لا يمكن تأكيد نقل المخزون للطلب %s\n"
                        "السبب: لم يتم إنشاء أي فواتير مرتبطة بأمر البيع"
                    ) % picking.sale_id.name)
                
                if payment_type == 'cash':
                    # التحقق من الفواتير المدفوعة بالكامل للعملاء النقديين
                    paid_invoices = picking.sale_id.invoice_ids.filtered(
                        lambda inv: inv.state == 'posted' and inv.payment_state == 'paid'
                    )
                    if not paid_invoices:
                        raise UserError(_(
                            "لا يمكن تأكيد نقل المخزون للطلب %s\n"
                            "السبب: العميل نقدي ولم يتم تسديد الفاتورة بالكامل\n"
                            "يرجى تأكيد دفع الفاتورة قبل متابعة عملية النقل"
                        ) % picking.sale_id.name)
                
                elif payment_type == 'credit':
                    # التحقق من وجود فاتورة مؤكدة للعملاء الآجلين
                    confirmed_invoices = picking.sale_id.invoice_ids.filtered(
                        lambda inv: inv.state == 'posted'
                    )
                    if not confirmed_invoices:
                        raise UserError(_(
                            "لا يمكن تأكيد نقل المخزون للطلب %s\n"
                            "السبب: العميل آجل ولم يتم تأكيد الفاتورة\n"
                            "يرجى تأكيد الفاتورة قبل متابعة عملية النقل"
                        ) % picking.sale_id.name)
                else:
                    raise UserError(_(
                        "نوع الدفع غير معروف لأمر البيع %s\n"
                        "يرجى تحديد نوع الدفع (نقدي/آجل) في أمر البيع"
                    ) % picking.sale_id.name)
                        
        return super(StockPicking, self).button_validate()
