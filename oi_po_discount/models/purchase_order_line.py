'''
Created on Jan 01, 2023

@author: Elyas
'''
from odoo import api, fields, models
from odoo.tools.float_utils import float_round

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    
    discount =  fields.Float(string="Discount (%)")
    price_before = fields.Float(digits='Product Price')
    
    @api.onchange('price_unit')
    def onchange_price_unit_set_discount(self):
        precision_digits = self.env['decimal.precision'].precision_get('Product Price')
        price_unit = float_round(self.price_before - (self.price_before * self.discount/100), precision_digits = precision_digits)
        if price_unit != self.price_unit:
            self.discount = 0
            self.price_before = self.price_unit
            
    
    @api.onchange('discount','price_before')
    def onchange_unit_price(self):
        self.price_unit = self.price_before - (self.price_before * self.discount/100)