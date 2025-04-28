# -*- coding: utf-8 -*-
from odoo import models, fields, api
from collections import defaultdict

class ProductProduct(models.Model):
    _inherit = 'product.product'

    has_duplicate_reference = fields.Boolean(
        string='Has Duplicate Internal Reference',
        compute='_compute_has_duplicate_reference',
        search='_search_has_duplicate_reference',
        help="Indicates if this product has duplicate internal references"
    )

    def _compute_has_duplicate_reference(self):
        """ Compute if product has duplicate internal reference """
        all_products = self.search([])
        code_dict = defaultdict(list)
        
        for product in all_products:
            if product.default_code:
                code_dict[product.default_code].append(product.id)
        
        for product in self:
            if product.default_code:
                product.has_duplicate_reference = len(code_dict.get(product.default_code, [])) > 1
            else:
                product.has_duplicate_reference = False

    def _search_has_duplicate_reference(self, operator, value):
        """ Search method for the has_duplicate_reference field """
        if operator not in ('=', '!=', '<>') or not isinstance(value, bool):
            return []
            
        self.env.cr.execute("""
            SELECT default_code 
            FROM product_product
            WHERE default_code IS NOT NULL
            GROUP BY default_code
            HAVING COUNT(id) > 1
        """)
        duplicate_codes = [r[0] for r in self.env.cr.fetchall()]
        
        if operator in ('=', '==') and value:
            return [('default_code', 'in', duplicate_codes)]
        elif operator in ('!=', '<>') or not value:
            return [('default_code', 'not in', duplicate_codes)]
        return []


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    has_duplicate_reference = fields.Boolean(
        string='Has Duplicate Internal Reference',
        compute='_compute_has_duplicate_reference',
        search='_search_has_duplicate_reference',
        help="Indicates if this product template has duplicate internal references"
    )

    def _compute_has_duplicate_reference(self):
        """ Compute if template has duplicate internal reference """
        all_templates = self.search([])
        code_dict = defaultdict(list)
        
        for template in all_templates:
            if template.default_code:
                code_dict[template.default_code].append(template.id)
        
        for template in self:
            if template.default_code:
                template.has_duplicate_reference = len(code_dict.get(template.default_code, [])) > 1
            else:
                template.has_duplicate_reference = False

    def _search_has_duplicate_reference(self, operator, value):
        """ Search method for the has_duplicate_reference field """
        if operator not in ('=', '!=', '<>') or not isinstance(value, bool):
            return []
            
        self.env.cr.execute("""
            SELECT default_code 
            FROM product_template
            WHERE default_code IS NOT NULL
            GROUP BY default_code
            HAVING COUNT(id) > 1
        """)
        duplicate_codes = [r[0] for r in self.env.cr.fetchall()]
        
        if operator in ('=', '==') and value:
            return [('default_code', 'in', duplicate_codes)]
        elif operator in ('!=', '<>') or not value:
            return [('default_code', 'not in', duplicate_codes)]
        return []
