from odoo import models, fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    partner_ref = fields.Char(string='مـرجـع المـورّد')
