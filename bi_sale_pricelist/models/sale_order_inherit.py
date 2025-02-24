# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
    
class SaleOrderLine(models.Model):
    _inherit="sale.order.line"
    pricelist_item_id = fields.Many2one(
        'product.pricelist.item',
        string="عنصر قائمة الأسعار",
        store=True  # إضافة هذا لجعل الحقل مخزن
    )
    def pricelist_apply(self):
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sale.order.pricelist.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
