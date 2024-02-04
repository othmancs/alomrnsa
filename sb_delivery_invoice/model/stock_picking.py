from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    invoice_id = fields.Many2one(related='sale_id.first_invoice_id', string='Invoice')
    invoice_date = fields.Date(related='sale_id.first_invoice_id.invoice_date')
