from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    ref = fields.Char(string='Reference', index=True, readonly=True, importable=True)

    # @api.constrains('vat')
    # def _check_unique_vat(self):
    #     for partner in self:
    #         if partner.vat:
    #             existing_partner = self.search([('vat', '=', partner.vat), ('id', '!=', partner.id)])
    #             if existing_partner:
    #                 raise ValidationError("Tax ID already exists!")

    def create(self, vals_list):
        for vals in vals_list:
            vals['ref'] = self.env['ir.sequence'].next_by_code('partner.reference.sequence')
            result = super(ResPartner, self).create(vals_list)
        return result
