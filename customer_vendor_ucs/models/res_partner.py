from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_customer = fields.Boolean(string="Is Customer")
    is_vendor = fields.Boolean(string="Is Vendor")

    @api.constrains('is_customer')
    def check_is_customer(self):
        for rec in self:
            if rec.is_customer and not rec.customer_rank:
                rec.customer_rank = 1

    @api.constrains('is_vendor')
    def check_is_customer(self):
        for rec in self:
            if rec.is_vendor  and not rec.supplier_rank:
                rec.supplier_rank = 1