from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    created_by_id = fields.Many2one('res.partner', string='انشأ من قبل')

