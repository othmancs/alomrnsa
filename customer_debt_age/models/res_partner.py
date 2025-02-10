from odoo import models, fields, api
from datetime import date

class ResPartner(models.Model):
    _inherit = 'res.partner'

    debt_age = fields.Integer(string='Debt Age (Days)', compute='_compute_debt_age', store=True)

    @api.depends('invoice_ids.invoice_date_due', 'invoice_ids.payment_state')
    def _compute_debt_age(self):
        for partner in self:
            unpaid_invoices = partner.invoice_ids.filtered(lambda inv: inv.payment_state in ('not_paid', 'partial'))
            if unpaid_invoices:
                oldest_invoice_date = min(unpaid_invoices.mapped('invoice_date_due'))
                partner.debt_age = (date.today() - oldest_invoice_date).days if oldest_invoice_date else 0
            else:
                partner.debt_age = 0
