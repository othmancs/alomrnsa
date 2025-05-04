from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    @api.constrains('uom_id')
    def _check_uom_category(self):
        for product in self:
            if product.uom_id.name == 'حبة':
                unit_category = self.env.ref('uom.product_uom_categ_unit', raise_if_not_found=False)
                if not unit_category or product.uom_id.category_id != unit_category:
                    raise ValidationError("وحدة القياس 'حبة' يجب أن تكون من فئة الوحدات (Unit)")
