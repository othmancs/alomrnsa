from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    total_purchase_price = fields.Float(string="TOTAL", compute="_compute_total_price")

    @api.depends('line_ids.purchase_price')
    def _compute_total_price(self):
        for record in self:
            record.total_purchase_price = sum(rec.purchase_price * rec.quantity for rec in record.line_ids)