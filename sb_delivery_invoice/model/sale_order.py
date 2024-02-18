from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    first_invoice_id = fields.Many2one('account.move', compute='compute_first_invoice', store=True)

    @api.depends('invoice_ids')
    def compute_first_invoice(self):
        for rec in self:
            if rec.invoice_ids:
                rec.first_invoice_id = rec.invoice_ids[0].id
