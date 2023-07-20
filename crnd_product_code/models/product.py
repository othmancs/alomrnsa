from openerp import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _get_default_product_code(self):
        return self.env['ir.sequence'].next_by_code('product.code')

    product_code = fields.Char(index=True, help='Product Code',
                               default=_get_default_product_code, copy=False)

    _sql_constraints = [
        ('product_product__product_code__uniq',
         'unique (product_code)',
         'Product code must be uniq!'),
    ]

    def action_set_product_code(self):
        for product in self:
            if not product.product_code:
                product.write({
                    'product_code': self._get_default_product_code(),
                })
        return True


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_code = fields.Char(store=True, index=True,
                               related='product_variant_ids.product_code',
                               readonly=True, help='Product code')

    def action_set_product_code(self):
        for tmpl in self.filtered(lambda r: len(r.product_variant_ids) == 1):
            tmpl.product_variant_ids[0].action_set_product_code()
        return True
