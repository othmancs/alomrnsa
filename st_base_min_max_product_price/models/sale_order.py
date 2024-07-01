# -*- coding: utf-8 -*-
# Email:smartthinkerstechne@gmail.com

from odoo import fields, models, api, _
from odoo.exceptions import UserError



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
  
    @api.onchange('price_unit','value_changed')
    def product_price_change(self):               
        if self.price_unit:          
            if (self.product_id.product_tmpl_id.st_pro_min_sale_price >0 and self.price_unit < self.product_id.product_tmpl_id.st_pro_min_sale_price) or (self.product_id.product_tmpl_id.st_pro_max_sale_price > 0 and self.price_unit > self.product_id.product_tmpl_id.st_pro_max_sale_price):

                
                warning_mess = {
                    'message': ('Price does not match with minnimum or maximum price !'),
                    'title': "Warning"
                }

                return {'warning': warning_mess}


    def write(self,values):       
        if 'price_unit' in values:        
            if (self.product_id.product_tmpl_id.st_pro_min_sale_price >0 and values['price_unit'] < self.product_id.product_tmpl_id.st_pro_min_sale_price) or (self.product_id.product_tmpl_id.st_pro_max_sale_price > 0 and values['price_unit'] > self.product_id.product_tmpl_id.st_pro_max_sale_price):
                    raise UserError(_("Price does not match with minnimum or maximum price !"))                    
            else:
                result = super(SaleOrderLine, self).write(values)
                return result
        else:
            result = super(SaleOrderLine, self).write(values)
            return result
    
    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:            
            if 'product_id' in values:
                product_obj = self.env['product.product'].sudo().search([('id','=',values['product_id'])],limit=1)           
                if 'price_unit' in values:               
                    if (product_obj.product_tmpl_id.st_pro_min_sale_price >0 and values['price_unit'] < product_obj.product_tmpl_id.st_pro_min_sale_price) or (product_obj.product_tmpl_id.st_pro_max_sale_price > 0 and values['price_unit'] > product_obj.product_tmpl_id.st_pro_max_sale_price):
                        raise UserError(_("Price does not match with minnimum or maximum price !"))
                    else:
                        res = super(SaleOrderLine, self).create(vals_list)
                        return res
                else:
                    res = super(SaleOrderLine, self).create(vals_list)
                    return res
            else:
                res = super(SaleOrderLine, self).create(vals_list)
                return res
