from odoo import models, fields, api

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def get_non_counted_products(self, inventory_id):
        """
        Returns products that exist in the inventory locations but weren't counted
        :param inventory_id: ID of the stock.inventory record
        :return: product.product recordset
        """
        inventory = self.env['stock.inventory'].browse(inventory_id)
        if not inventory.exists():
            return self.env['product.product']
            
        # Get all products in the inventory locations
        domain = [
            ('location_id', 'child_of', inventory.location_id.id),
            ('product_id.type', '=', 'product'),
        ]
        if inventory.product_id:
            domain.append(('product_id', 'in', inventory.product_id.ids))
            
        all_products = self.search(domain).mapped('product_id')
        
        # Get counted products
        counted_products = inventory.line_ids.mapped('product_id')
        
        # Non-counted products are those in all_products but not in counted_products
        return all_products - counted_products


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    non_counted_products = fields.Many2many(
        'product.product',
        string='Non Counted Products',
        compute='_compute_non_counted_products',
        store=False,
        help="Products that existed in inventory locations but weren't counted"
    )

    non_counted_count = fields.Integer(
        string='Non Counted Products Count',
        compute='_compute_non_counted_products',
        store=False
    )

    @api.depends('state', 'line_ids', 'location_id', 'product_id')
    def _compute_non_counted_products(self):
        for inventory in self:
            if inventory.state == 'done':
                non_counted = self.env['stock.quant'].get_non_counted_products(inventory.id)
                inventory.non_counted_products = non_counted
                inventory.non_counted_count = len(non_counted)
            else:
                inventory.non_counted_products = False
                inventory.non_counted_count = 0

    def action_show_non_counted_products(self):
        self.ensure_one()
        return {
            'name': 'Non Counted Products',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'product.product',
            'domain': [('id', 'in', self.non_counted_products.ids)],
            'context': dict(self.env.context, create=False),
            'target': 'current',
        }
class ProductProduct(models.Model):
    _inherit = 'product.product'

    equipment_company_id = fields.Many2one(
        'res.company', 
        string='Equipment Company'
    )
    qr_code = fields.Char(
        string='QR Code',
        help="Product QR Code"
    )
