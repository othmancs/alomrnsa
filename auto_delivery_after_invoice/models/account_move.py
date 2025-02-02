
from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super(AccountMove, self).action_post()

        # التحقق مما إذا كانت الفاتورة مرتبطة بأمر مبيعات
        for invoice in self:
            if invoice.move_type == 'out_invoice' and invoice.invoice_origin:
                sale_order = self.env['sale.order'].search([('name', '=', invoice.invoice_origin)], limit=1)
                if sale_order:
                    sale_order.action_confirm()  # تأكيد أمر البيع إذا لم يكن مؤكدًا

                    for picking in sale_order.picking_ids:
                        if picking.state in ['waiting', 'confirmed']:
                            picking.action_assign()  # تخصيص المخزون
                            picking.button_validate()  # تأكيد التوصيل

        return res
