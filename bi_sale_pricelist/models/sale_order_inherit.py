# # -*- coding: utf-8 -*-
# # Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

# from odoo import api, fields, models, _
    
# class SaleOrderLine(models.Model):
#     _inherit="sale.order.line"
    
#     def pricelist_apply(self):
#         return {
#                 'view_type': 'form',
#                 'view_mode': 'form',
#                 'res_model': 'sale.order.pricelist.wizard',
#                 'type': 'ir.actions.act_window',
#                 'target': 'new',
#             }
# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    @api.constrains('product_id', 'product_uom_qty')
    def _check_pricelist(self):
        for line in self:
            if not line.order_id.pricelist_id:
                continue

            # التحقق من وجود الطريقة المناسبة لحساب السعر
            pricelist = line.order_id.pricelist_id
            product = line.product_id
            quantity = line.product_uom_qty
            partner = line.order_id.partner_id

            # محاولة استخدام الطريقة المناسبة لحساب السعر
            try:
                if hasattr(pricelist, 'get_product_price'):
                    product_price = pricelist.get_product_price(product, quantity, partner)
                elif hasattr(pricelist, '_get_combination_price'):
                    product_price = pricelist._get_combination_price(product, quantity, partner)
                else:
                    raise ValidationError("طريقة حساب السعر غير مدعومة في القائمة السعرية.")
            except Exception as e:
                raise ValidationError(f"حدث خطأ أثناء حساب السعر: {str(e)}")

            # التحقق من الشرط (كمثال)
            if product_price <= 0:
                raise ValidationError(f"السعر المحسوب للمنتج {product.display_name} لا يمكن أن يكون صفرًا أو أقل.")
