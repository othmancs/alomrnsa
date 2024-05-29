from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Description'

    # def _compute_product_pricelist(self):
    #     res = self.env['product.pricelist']._get_partner_pricelist_multi(self.ids)
    #     for partner in self:
    #         partner.property_product_pricelist = res.get(partner._origin.id)

    @api.model
    def create_partner_with_sudo(self, vals):
        return self.sudo().create(vals).id
