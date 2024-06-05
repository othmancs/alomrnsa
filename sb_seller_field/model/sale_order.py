from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    seller_id = fields.Many2one('res.partner', string='اسم البائع', domain="[('branch_id', '=', branch_id)]")

