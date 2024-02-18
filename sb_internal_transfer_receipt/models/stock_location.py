from odoo import fields, models, api


class StockLocation(models.Model):
    _inherit = 'stock.location'

    is_transit_location = fields.Boolean()
