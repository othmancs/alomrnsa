from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    inventory_id = fields.Many2one(
        "stock.inventory", "Stock Inventory", check_company=True
    )
