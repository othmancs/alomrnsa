# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare

class ProductKit(models.Model):
    _name = 'product.kit'
    _description = "Product Kit"
    
    product_id = fields.Many2one(
        'product.product', 
        string='Product', 
        required=True,
        domain="[('id', '!=', parent.product_id)]"
    )
    qty_uom = fields.Float(
        string='Quantity', 
        required=True, 
        default=1.0,
        digits='Product Unit of Measure'
    )
    bi_product_template = fields.Many2one(
        'product.template', 
        string='Product Pack',
        ondelete='cascade'
    )
    bi_cost = fields.Float(
        related='product_id.standard_price', 
        string='Cost', 
        store=True,
        digits='Product Price'
    )
    bi_list_price = fields.Float(
        related='product_id.list_price', 
        string='Public Price', 
        store=True,
        digits='Product Price'
    )
    price = fields.Float(
        related='product_id.lst_price', 
        string='Product Price',
        digits='Product Price'
    )
    uom_id = fields.Many2one(
        related='product_id.uom_id', 
        string="Unit of Measure", 
        readonly=True
    )
    name = fields.Char(
        related='product_id.name', 
        readonly=True
    )

    _sql_constraints = [
        ('positive_qty', 'CHECK(qty_uom > 0)', 'Quantity must be strictly positive'),
        ('unique_product_kit', 'unique(product_id, bi_product_template)', 
         'This product is already in the kit!'),
    ]


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_kit = fields.Boolean(
        string='Use as Kit',
        help="Check this box if this product is a kit/pack"
    )
    cal_kit_price = fields.Boolean(
        string='Calculate Kit Price',
        help="Automatically calculate price based on kit components"
    )
    kit_ids = fields.One2many(
        'product.kit', 
        'bi_product_template', 
        string='Kit Components',
        copy=True
    )

    @api.constrains('is_kit', 'kit_ids')
    def _check_kit_components(self):
        for product in self:
            if product.is_kit and not product.kit_ids:
                raise ValidationError(_("A kit product must have at least one component."))

    @api.model_create_multi
    def create(self, vals_list):
        records = super(ProductTemplate, self).create(vals_list)
        for record in records:
            if record.cal_kit_price:
                record._compute_kit_price()
        return records

    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        if 'kit_ids' in vals or 'cal_kit_price' in vals:
            for product in self:
                if product.cal_kit_price:
                    product._compute_kit_price()
        return res

    def _compute_kit_price(self):
        self.ensure_one()
        total = 0.0
        for kit_line in self.kit_ids:
            total += kit_line.qty_uom * kit_line.product_id.list_price
        if total > 0:
            self.list_price = total

    def _compute_sales_count(self):
        """ Override to handle kit products properly """
        for product in self:
            if product.is_kit:
                # For kit products, sum sales of all variants
                product.sales_count = float_round(
                    sum(p.sales_count for p in product.with_context(
                        active_test=False).product_variant_ids),
                    precision_rounding=product.uom_id.rounding
                )
            else:
                # Default computation for regular products
                super(ProductTemplate, product)._compute_sales_count()


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _compute_sales_count(self):
        """ Override to handle kit products properly """
        kit_products = self.filtered(lambda p: p.is_kit)
        for product in kit_products:
            product.sales_count = 0.0  # Kit products get count from template
        
        # Default computation for regular products
        super(ProductProduct, self - kit_products)._compute_sales_count()


class SaleReport(models.Model):
    _inherit = 'sale.report'

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        """ Fix UNION query by ensuring consistent columns """
        fields['product_kit'] = ", l.product_id as product_kit"
        groupby += ', l.product_id'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)


class StockMove(models.Model):
    _inherit = 'stock.move'

    pack_id = fields.Many2one(
        'product.kit',
        string="Kit Component",
        help="Indicates which kit component this move corresponds to"
    )


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    pack_id = fields.Many2one(
        'product.kit',
        string="Kit Component",
       
