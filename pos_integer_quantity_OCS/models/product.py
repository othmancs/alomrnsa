from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    @api.constrains('uom_id')
    def _check_uom_category(self):
        for product in self:
            if product.uom_id.name == 'حبة' and product.uom_id.category_id.measure_type != 'unit':
                raise ValidationError("وحدة القياس 'حبة' يجب أن تكون من فئة الوحدات (Unit)")