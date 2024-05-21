from odoo import models, fields, api


class ProductBranchTemplate(models.Model):
    _inherit = 'product.template'

    many_branch_product_ids = fields.Many2many(
        'res.branch',
        'product_template_many_branch_rel',
        string="All Branches",

    )

