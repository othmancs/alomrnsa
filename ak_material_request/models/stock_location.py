from odoo import api, fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    branch_id = fields.Many2one('res.branch')
