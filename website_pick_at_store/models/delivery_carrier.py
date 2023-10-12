from odoo import api, fields, models, _

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    personal_store_pickup = fields.Boolean(
        string='Pickup at Store?')
    store_type = fields.Selection([
        ('all', 'All Stores'),
        ('available', 'Store enough qty')
    ], default='all')
    warehouse_ids = fields.Many2many(
        'stock.warehouse', string="Stores / Warehouses"
    )

    def get_available_stores(self, order):
        self.ensure_one()
        warehouses = self.env['stock.warehouse']
        if self.personal_store_pickup:
            warehouses = self.warehouse_ids
            if not warehouses:
                warehouses = self.env['stock.warehouse'].search(
                    [('is_store', '=', True), ('partner_id', '!=', False)])
            else:
                warehouses = warehouses.filtered(
                    lambda s: s.is_store and s.partner_id)
        if self.store_type == 'available':
            warehouses = self._filter_available(warehouses, order)
        return warehouses.get_name_and_address()

    def _filter_available(self, warehouses, order):
        res = warehouses
        for warehouse in warehouses:
            loc = warehouse.lot_stock_id
            for line in order.order_line:
                product = line.product_id
                if product.type == 'product':
                    qty = product.with_context(
                        location=loc.id, warehouse=None).qty_available
                    if line.product_uom_qty > qty:
                        # No enough stock on hand
                        res -= warehouse
                        break
        return res
