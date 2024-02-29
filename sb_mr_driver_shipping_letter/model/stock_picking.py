from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    driver_id = fields.Many2one(related='request_id.driver_id')
    lading_number = fields.Char(related='request_id.lading_number')


