# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'



    def _domain_industry_id(self):
        partner_search_mode = self.env.context.get('res_partner_search_mode')
        if partner_search_mode not in ('customer', 'supplier'):
            return f"[]"

        if partner_search_mode == 'customer':
            domain = "('is_customer', '!=', False)"
        else:
            domain = "('is_vendor', '!=', False)"

        return f"[{domain}]"

    industry_id=fields.Many2one('res.partner.industry',string="Industry",domain=lambda self: self._domain_industry_id())
    partner_c=fields.Char(string="Partner Code",readonly='True')


    @api.model_create_multi
    def create(self, vals_list):
        print("1"*30,vals_list)
        for vals in vals_list:
            if vals.get('company_type'):
                if vals['company_type'] == 'company':
                    if vals.get('industry_id'):
                        indus_id = self.env['res.partner.industry'].browse(int(vals['industry_id']))
                        vals['partner_c'] = indus_id._get_sequence_number()
        return super().create(vals_list)

    # def write(self, values):
    #     if 'industry_id' in values:
    #         indus_id = self.env['res.partner.industry'].browse(int(values['industry_id']))
    #         if indus_id:
    #             values['partner_c'] = indus_id._get_sequence_number()
    #     res = super(ResPartner, self).write(values)
    #     return res


