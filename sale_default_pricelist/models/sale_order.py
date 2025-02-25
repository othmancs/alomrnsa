from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _default_pricelist(self):
        return self.env.ref('__export__.product_pricelist_101_d50a1655', raise_if_not_found=False) or self.env['product.pricelist'].search([], limit=1).id

    pricelist_id = fields.Many2one(
        'product.pricelist',
        string="Pricelist",
        default=_default_pricelist,
        required=True
    )
