from odoo import models, api
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.constrains('order_line')
    def _check_order_lines(self):
        """
        Prevent saving the sale order if there are no order lines.
        """
        for order in self:
            if not order.order_line:
                raise UserError("لا يمكنك حفظ أمر بيع بدون بنود.")
