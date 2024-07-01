from odoo import fields, models


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    branch_id = fields.Many2one('res.branch', string='Branch')
    created_by_id = fields.Many2one('res.partner', string='انشأ من قبل', domain="[('branch_id', '=', branch_id)]")
