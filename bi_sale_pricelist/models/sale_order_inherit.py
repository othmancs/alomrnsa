# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
    
class SaleOrderLine(models.Model):
    _inherit="sale.order.line"
    pricelist_item_id = fields.Many2one(
        'product.pricelist.item',
        string="عنصر قائمة الأسعار",
        store=True
    )
    
    def pricelist_apply(self):
        return {
            'name': _("Pricelist Wizard"),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sale.order.pricelist.wizard',
            'target': 'new',
            'context': {
                'default_line_id': self.id,
                'active_ids': [self.id],
            }
        }
