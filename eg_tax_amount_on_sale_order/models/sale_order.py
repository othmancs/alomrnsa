from odoo import fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"
    _description = "Sale Order"

    print_tax_amount_in_sale = fields.Boolean(string="Print Tax Amount")