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

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.constrains('price_unit')
    def _check_pricelist(self):
        for line in self:
            if line.order_id.pricelist_id:
                product_price = line.order_id.pricelist_id._compute_price(
                    line.product_id.id, 
                    line.product_uom_qty, 
                    line.order_id.partner_id
                )
                if line.price_unit < product_price:
                    raise ValidationError(_(
                        "The price for the product '%s' cannot be lower than the pricelist price (%.2f)." % (
                            line.product_id.name, product_price)))

    def pricelist_apply(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order.pricelist.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
