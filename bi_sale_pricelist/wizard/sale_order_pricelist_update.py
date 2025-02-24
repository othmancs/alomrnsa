# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from datetime import date
from odoo.exceptions import UserError

class SaleOrderPricelistWizard(models.TransientModel):  # استخدام TransientModel بدلاً من Model
    _name = 'sale.order.pricelist.wizard'
    _description = 'Pricelist Wizard'
    
    bi_wizard_pricelist_id = fields.Many2one('product.pricelist', string="Pricelist")
    pricelist_line = fields.One2many('sale.order.pricelist.wizard.line', 'pricelist_id', string='Pricelist Line Id')

    @api.model
    def default_get(self, fields):
        res = super(SaleOrderPricelistWizard, self).default_get(fields)
        res_ids = self._context.get('active_ids')

        if res_ids:
            so_line = self.env['sale.order.line'].browse(res_ids[0])

            # التحقق مما إذا كان سطر أمر البيع موجودًا لتجنب الأخطاء
            if not so_line.exists():
                raise UserError("لا يمكن العثور على سطر أمر البيع.")

            pricelist_data = []

            # البحث عن قوائم الأسعار التي تحتوي على المنتج الحالي
            pricelists = self.env['product.pricelist'].sudo().search([
                ('item_ids.product_tmpl_id', '=', so_line.product_id.product_tmpl_id.id)
            ])

            if pricelists:
                for pricelist in pricelists:
                    price_rule = pricelist._compute_price_rule(
                        so_line.product_id,
                        so_line.product_uom_qty,
                        date=date.today(),
                        uom_id=so_line.product_uom.id
                    )
                    price_unit = price_rule.get(so_line.product_id.id, [0])[0]

                    if price_unit != 0.0:
                        margin = price_unit - so_line.product_id.standard_price
                        margin_per = (100 * margin) / price_unit if price_unit else 0.0

                        pricelist_data.append((0, 0, {
                            'bi_pricelist_id': pricelist.id,
                            'bi_unit_price': price_unit,
                            'bi_unit_measure': so_line.product_uom.id,
                            'bi_unit_cost': so_line.product_id.standard_price,
                            'bi_margin': margin,
                            'bi_margin_per': margin_per,
                        }))

            res.update({
                'pricelist_line': pricelist_data,
            })
        return res


class SaleOrderPricelistWizardLine(models.TransientModel):  # استخدام TransientModel هنا أيضًا
    _name = 'sale.order.pricelist.wizard.line'
    _description = 'Pricelist Wizard Line'

    pricelist_id = fields.Many2one('sale.order.pricelist.wizard', "Pricelist Id")
    bi_pricelist_id = fields.Many2one('product.pricelist', "Pricelist", required=True)
    bi_unit_measure = fields.Many2one('uom.uom', 'Unit')
    bi_unit_price = fields.Float('Unit Price')
    bi_unit_cost = fields.Float('Unit Cost')
    bi_margin = fields.Float('Margin')
    bi_margin_per = fields.Float('Margin %')
    line_id = fields.Many2one('sale.order.line', string="Sale Order Line")
