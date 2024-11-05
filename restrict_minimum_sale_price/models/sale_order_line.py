from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('price_unit')
    def _check_price_unit_against_pricelist(self):
        if self.order_id.pricelist_id and self.product_id:
            # الحصول على السعر من قائمة الأسعار المختارة
            pricelist_price = self.order_id.pricelist_id.get_product_price(self.product_id, self.product_uom_qty or 1.0,
                                                                           self.order_id.partner_id)

            if self.price_unit < pricelist_price:
                # عرض رسالة خطأ في حال كان السعر أقل من السعر في قائمة الأسعار
                raise UserError(
                    "The sale price cannot be lower than the selected pricelist price of %s." % pricelist_price)
