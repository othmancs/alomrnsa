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
        wizard = self.env['sale.order.pricelist.wizard'].create({
            'bi_wizard_pricelist_id': self.pricelist_id.id  # ربط المعالج بسجل معين
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.pricelist.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
        }

