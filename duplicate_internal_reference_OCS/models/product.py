from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'

    has_duplicate_reference = fields.Boolean(
        string='Has Duplicate Internal Reference',
        compute='_compute_has_duplicate_reference',
        search='_search_has_duplicate_reference'
    )

    def _compute_has_duplicate_reference(self):
        for product in self:
            if product.default_code:
                same_code_count = self.search_count([
                    ('default_code', '=', product.default_code),
                    ('id', '!=', product.id)
                ])
                product.has_duplicate_reference = same_code_count > 0
            else:
                product.has_duplicate_reference = False

    def _search_has_duplicate_reference(self, operator, value):
        if operator not in ('=', '!=') or not isinstance(value, bool):
            return []
        
        self.env.cr.execute("""
            SELECT default_code
            FROM product_product
            WHERE default_code IS NOT NULL
            GROUP BY default_code
            HAVING COUNT(id) > 1
        """)
        duplicate_codes = [r[0] for r in self.env.cr.fetchall()]
        
        if (operator == '=' and value) or (operator == '!=' and not value):
            return [('default_code', 'in', duplicate_codes)]
        else:
            return [('default_code', 'not in', duplicate_codes)]