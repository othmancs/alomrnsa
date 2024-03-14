from odoo import fields, models, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    parent_location_id = fields.Many2one(related='location_id.location_id')
