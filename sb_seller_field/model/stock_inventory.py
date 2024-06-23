from odoo import fields, models


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    created_by_id = fields.Many2one('res.partner', string='انشأ من قبل')

