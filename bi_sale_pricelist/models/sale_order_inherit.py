# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    pricelist_item_id = fields.Many2one('product.pricelist.item', string="عنصر قائمة الأسعار", store=True)

    def get_pricelist_tooltip_info(self):
        self.ensure_one()
        if not self.product_id:
            return "لا يوجد منتج محدد"
        
        pricelists = self.env['product.pricelist'].search([
            ('item_ids.product_tmpl_id', '=', self.product_id.product_tmpl_id.id)
        ])
        
        tooltip_lines = []
        for pricelist in pricelists:
            price = pricelist._compute_price_rule(
                self.product_id,
                self.product_uom_qty or 1,
                date=fields.Date.today(),
                uom_id=self.product_uom.id
            ).get(self.product_id.id, [0])[0]
            
            if price > 0:
                tooltip_lines.append(
                    f"{pricelist.name}: {price:.2f} {self.order_id.currency_id.symbol}"
                )
        
        return "\n".join(tooltip_lines) if tooltip_lines else "لا توجد أسعار متاحة"
