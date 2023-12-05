from odoo import models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def name_get(self):
        return [(rec.id, rec.name) for rec in self]
