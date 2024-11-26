from odoo import models, fields


class OrderlineProductStockInfo(models.TransientModel):
    _name = "orderline.product.stock.info"
    _description = 'Sale order line product stock info'

    product_id = fields.Many2one('product.product', string="Product", readonly=True, required=True)
    orderline_product_stock_info_ids = fields.One2many("orderline.product.stock.info.line",
                                                       "orderline_product_stock_info_id",
                                                       string="Stock Lines")


class OrderlineProductStockInfoLine(models.TransientModel):
    _name = "orderline.product.stock.info.line"
    _rec_name = "orderline_product_stock_info_id"
    _description = 'Sale order line product stock info line'

    orderline_product_stock_info_id = fields.Many2one("orderline.product.stock.info", string="Stock Information")
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse", readonly=True)
    location_id = fields.Many2one('stock.location', string="Location", readonly=True)
    qty_available = fields.Float("On Hand", readonly=True)
    incoming_qty = fields.Float("Incoming", readonly=True)
    outgoing_qty = fields.Float("Outgoing", readonly=True)
    virtual_available = fields.Float("Forecast", readonly=True)
    free_qty = fields.Float("Real Stock in Warehouse", readonly=True)
