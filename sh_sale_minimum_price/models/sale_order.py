
# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api, _
from odoo.tools.misc import get_lang
from odoo.exceptions import UserError
from odoo import Command


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        if self:
            if self.order_line:
                down_price_lines = self.order_line.filtered(lambda x: x.price_unit < x.sh_sale_minimum_price).sorted('price_unit')
                if down_price_lines:
                    message=""
                    for line in down_price_lines:
                        message+="Unit price less than minimum price of " + str(line.product_template_id.name_get()[0][1]) + '\n'
                    if message!="":
                        raise UserError(message)
        return super(SaleOrder, self).action_confirm()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    sh_sale_minimum_price = fields.Float("Minimum Price",readonly=True)

    @api.onchange('product_id')
    def _onchange_product_id_warning(self):
        super(SaleOrderLine, self)._onchange_product_id_warning()
        if not self.product_id:
            return
        vals = {}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = self.product_uom_qty or 1.0

        product = self.product_id.with_context(
            lang=get_lang(self.env, self.order_id.partner_id.lang).code,
            partner=self.order_id.partner_id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        vals.update(name=self._get_sale_order_line_multiline_description_sale())

        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['sh_sale_minimum_price'] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(), product.taxes_id, self.tax_id, self.company_id)
        self.update(vals)

    # @api.depends('product_id', 'product_uom','product_uom_qty')
    # def _compute_price_unit(self):
    #     res = super(SaleOrderLine, self)._compute_price_unit()
    #     if self.order_id.pricelist_id and self.order_id.partner_id:
    #         self.sh_sale_minimum_price = self.price_unit
    #     return res

    @api.onchange('price_unit')
    def price_unit_check(self):
        if self.price_unit < self.sh_sale_minimum_price:
            warning_mess = {
                'title': _('Message'),
                'message' : _("Unit Price is less than Minimum Price."),
            }
            return {'warning': warning_mess}
