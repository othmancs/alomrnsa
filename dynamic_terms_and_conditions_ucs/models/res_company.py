# -*- coding:utf-8 -*-

from odoo import fields, models, api

class ResCompany(models.Model):

    _inherit = 'res.company'

    dynamic_sale_terms = fields.Html('Sale Terms & Condition')
    dynamic_purchase_terms = fields.Html('Purchase Terms & Condition')
    dynamic_invoice_terms = fields.Html('Customer Invoice Terms & Condition')
    is_same = fields.Boolean("Same as a Sale Terms & Condition")
    is_global = fields.Boolean("Is Global Terms")

    @api.constrains('is_same')
    def check_is_same(self):
        for company in self:
            if company.is_same == True:
                company.dynamic_purchase_terms = company.dynamic_sale_terms
                company.dynamic_invoice_terms = company.dynamic_sale_terms


class ResConfigSettings(models.TransientModel):
    
    _inherit = 'res.config.settings'

    is_global = fields.Boolean("Is Global Terms", related='company_id.is_global', readonly=False)
