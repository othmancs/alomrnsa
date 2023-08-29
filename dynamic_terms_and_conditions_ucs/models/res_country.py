# -*- coding:utf-8 -*-

from odoo import fields, models, api


class ResCountry(models.Model):

    _inherit = 'res.country'

    dynamic_sale_terms = fields.Html('Sale Terms & Condition')
    dynamic_purchase_terms = fields.Html('Purchase Terms & Condition')
    dynamic_invoice_terms = fields.Html('Customer Invoice Terms & Condition')
    is_same = fields.Boolean("Same as a Sale Terms & Condition")

    @api.constrains('is_same')
    def check_is_same(self):
        for country in self:
            if country.is_same == True:
                country.dynamic_purchase_terms = country.dynamic_sale_terms
                country.dynamic_invoice_terms = country.dynamic_sale_terms
