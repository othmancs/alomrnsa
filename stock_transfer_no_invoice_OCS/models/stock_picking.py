from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        for picking in self:
            if picking.sale_id:  # إذا كان هناك أمر بيع مرتبط
                payment_type = picking.sale_id.payment_type  # جلب نوع الدفع من أمر البيع
                
                if payment_type == 'cash':
                    # التحقق من الفواتير المدفوعة بالكامل
                    paid_invoices = picking.sale_id.invoice_ids.filtered(
                        lambda inv: inv.state == 'posted' and inv.payment_state == 'paid'
                    )
                    if not paid_invoices:
                        raise UserError(_(
                            "لا يمكن تأكيد نقل المخزون للطلب %s\n"
                            "السبب: العميل نقدي ولم يتم تسجيل السداد الكامل للفاتورة"
                        ) % picking.sale_id.name)
                
                elif payment_type == 'credit':
                    # التحقق من وجود فاتورة مؤكدة (حتى لو غير مدفوعة)
                    confirmed_invoices = picking.sale_id.invoice_ids.filtered(
                        lambda inv: inv.state == 'posted'
                    )
                    if not confirmed_invoices:
                        raise UserError(_(
                            "لا يمكن تأكيد نقل المخزون للطلب %s\n"
                            "السبب: العميل آجل ولم يتم إنشاء فاتورة مؤكدة"
                        ) % picking.sale_id.name)
                        
        return super(StockPicking, self).button_validate()
