# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models
from odoo.tools.float_utils import float_round as round


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    warranty_details = fields.One2many('warranty.detail', 'sale_id', string="Warranty Info")

    def action_confirm(self):
        """
            Override method for create warranty records
        """
        res = super(SaleOrder, self).action_confirm()
        context = dict(self.env.context)
        if not context.get('from_repair'):
            for line in self.order_line.filtered(lambda l: l.product_id.tracking == 'serial'):
                if line.product_id.warranty_id:
                    for qty in range(int(round(line.product_uom_qty,0))):
                        warranty_id = self.env['warranty.detail'].create({
                                'sale_id': line.order_id.id,
                                'sale_line_id': line.id,
                                'product_id': line.product_id.id,
                                'template_id': line.product_id.warranty_id.id,
                                'partner_id': line.order_id.partner_id.id,
                                'partner_phone': line.order_id.partner_id.phone,
                                'partner_email': line.order_id.partner_id.email,
                                'user_id': line.order_id.user_id.id or self.env.user.id,
                                'warranty_info': line.product_id.warranty_id.warranty_info,
                                'warranty_tc': line.product_id.warranty_id.warranty_tc,
                                'tag_ids': [(6, 0, line.order_id.tag_ids.ids)],
                        })
                        warranty_id.action_pending()
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    warranty_details = fields.One2many('warranty.detail', 'sale_line_id', string="Warranty Info")
