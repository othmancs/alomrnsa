from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    created_by_id = fields.Many2one('res.partner', string='انشأ من قبل', domain="[('branch_id', '=', branch_id)]")

