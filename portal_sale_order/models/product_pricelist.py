from odoo import fields, models, api


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    @api.model
    def get_product_price_rpc(self, product_id, quantity, pricelist_id):
        pricelist = self.browse(pricelist_id)
        product = self.env['product.product'].browse(product_id)

        return pricelist._get_product_price(product, quantity)

