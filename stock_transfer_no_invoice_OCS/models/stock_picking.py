from odoo import models, api, fields, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def create(self, vals):
        picking = super(StockPicking, self).create(vals)
        return picking

    def button_validate(self):
        for picking in self:
            if picking.sale_id:
                invoices = picking.sale_id.invoice_ids.filtered(
                    lambda inv: inv.state == 'posted'
                )
                if not invoices:
                    raise UserError(_(
                        "لا يمكن تأكيد نقل المخزون لأنه لم يتم تأكيد أي فاتورة مرتبطة بأمر البيع %s."
                    ) % picking.sale_id.name)
        return super(StockPicking, self).button_validate()