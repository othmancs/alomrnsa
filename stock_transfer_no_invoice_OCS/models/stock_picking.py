from odoo import models, api, fields, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        for picking in self:
            if picking.sale_id:  # إذا كان هناك أمر بيع مرتبط بنقل المخزون
                # جلب نوع الدفع (كاش أو آجل)
                payment_type = picking.sale_id.payment_term_id.payment_type if picking.sale_id.payment_term_id else False
                
                if payment_type == 'cash':
                    # في حالة الدفع كاش - نتحقق من وجود سداد مدفوع
                    invoices = picking.sale_id.invoice_ids.filtered(
                        lambda inv: inv.state == 'posted' and inv.payment_state in ('paid', 'in_payment')
                    )
                    if not invoices:
                        raise UserError(_(
                            "لا يمكن تأكيد نقل المخزون لأنه لم يتم تسجيل الدفع لأي فاتورة مرتبطة بأمر البيع %s."
                        ) % picking.sale_id.name)
                
                elif payment_type == 'credit':
                    # في حالة الدفع آجل - نتحقق فقط من وجود فاتورة مؤكدة
                    invoices = picking.sale_id.invoice_ids.filtered(
                        lambda inv: inv.state == 'posted'
                    )
                    if not invoices:
                        raise UserError(_(
                            "لا يمكن تأكيد نقل المخزون لأنه لم يتم تأكيد أي فاتورة مرتبطة بأمر البيع %s."
                        ) % picking.sale_id.name)
                
                else:
                    # الحالة الافتراضية إذا لم يتم تحديد نوع الدفع
                    invoices = picking.sale_id.invoice_ids.filtered(
                        lambda inv: inv.state == 'posted'
                    )
                    if not invoices:
                        raise UserError(_(
                            "لا يمكن تأكيد نقل المخزون لأنه لم يتم تأكيد أي فاتورة مرتبطة بأمر البيع %s."
                        ) % picking.sale_id.name)
                        
        return super(StockPicking, self).button_validate()
