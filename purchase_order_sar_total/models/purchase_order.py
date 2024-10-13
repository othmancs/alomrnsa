from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    total_in_sar = fields.Monetary(string="Total in SAR", compute='_compute_total_in_sar', currency_field='company_currency_id', readonly=True)

    company_currency_id = fields.Many2one('res.currency', string="Company Currency", related='company_id.currency_id', readonly=True)

    @api.depends('amount_total', 'currency_id')
    def _compute_total_in_sar(self):
        for order in self:
            company_currency = order.company_currency_id
            if order.currency_id != company_currency:
                # تحويل إجمالي الدولار إلى الريال السعودي
                order.total_in_sar = order.currency_id._convert(
                    order.amount_total, company_currency, order.company_id, order.date_order or fields.Date.today())
            else:
                order.total_in_sar = order.amount_total
