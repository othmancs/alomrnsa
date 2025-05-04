# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, float_round

class ProductKit(models.Model):
    _name = 'product.kit'
    _description = "Product Kit"
    _order = "sequence, id"
    
    sequence = fields.Integer(string="Sequence", default=1)
    product_id = fields.Many2one(
        'product.product', 
        string='Product', 
        required=True,
        domain="[('id', '!=', parent.product_id)]",
        help="Product component of the kit"
    )
    qty_uom = fields.Float(
        string='Quantity', 
        required=True, 
        default=1.0,
        digits='Product Unit of Measure',
        help="Quantity needed for this component"
    )
    bi_product_template = fields.Many2one(
        'product.template', 
        string='Product Pack',
        ondelete='cascade',
        help="Parent kit product"
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
        copy=True,
        help="List of products included in this kit"
    )

    @api.constrains('is_kit', 'kit_ids')
    def _check_kit_components(self):
        """Validate kit configuration"""
        for product in self:
            if product.is_kit and not product.kit_ids:
                raise ValidationError(_("A kit product must have at least one component."))
            if product.is_kit and product in product.kit_ids.product_id.product_tmpl_id:
                raise ValidationError(_("A kit cannot contain itself as a component."))

    @api.model_create_multi
    def create(self, vals_list):
        """Handle kit price calculation on creation"""
        records = super().create(vals_list)
        records.filtered(lambda r: r.cal_kit_price)._compute_kit_price()
        return records

    def write(self, vals):
        """Handle kit price calculation on update"""
        res = super().write(vals)
        if 'kit_ids' in vals or 'cal_kit_price' in vals:
            self.filtered(lambda p: p.cal_kit_price)._compute_kit_price()
        return res

    def _compute_kit_price(self):
        """Calculate kit price based on components"""
        for product in self:
            if not product.cal_kit_price:
                continue
                
            total = 0.0
            for kit_line in product.kit_ids:
                total += kit_line.qty_uom * kit_line.product_id.list_price
            
            if total > 0:
                product.list_price = total

    def _compute_sales_count(self):
        """Custom sales count computation for kits"""
        kit_products = self.filtered(lambda p: p.is_kit)
        
        # Handle regular products first
        super(ProductTemplate, self - kit_products)._compute_sales_count()
        
        # Handle kit products
        for product in kit_products:
            try:
                product.sales_count = float_round(
                    sum(p.sales_count for p in product.with_context(
                        active_test=False).product_variant_ids),
                    precision_rounding=product.uom_id.rounding
                )
            except Exception as e:
                product.sales_count = 0.0
                _logger.error("Error computing sales count for kit %s: %s", product.id, str(e))


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _compute_sales_count(self):
        """Custom sales count computation for kit variants"""
        kit_products = self.filtered(lambda p: p.is_kit)
        
        # Kit variants get count from template
        kit_products.update({'sales_count': 0.0})
        
        # Handle regular products
        super(ProductProduct, self - kit_products)._compute_sales_count()


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
        help="Indicates which kit component this move line corresponds to"
    )
