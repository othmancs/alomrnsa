from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    company_currency_id = fields.Many2one(
        'res.currency',
        string="Company Currency",
        related='company_id.currency_id',
        readonly=True
    )

    landed_cost_total = fields.Float(
        string='صافي التكلفة',
        compute='_compute_landed_cost_total',
        store=True
    )

    total_in_sar = fields.Monetary(
        string="الإجمالي بالريال",
        compute='_compute_total_in_sar',
        currency_field='company_currency_id',
        readonly=True,
        store=True
    )

    total_supplier_cost = fields.Monetary(
        string="إجمالي المورد",
        compute="_compute_total_supplier_cost",
        store=True,
        currency_field='company_currency_id'
    )

    @api.depends('invoice_ids', 'invoice_ids.state')
    def _compute_landed_cost_total(self):
        for order in self:
            total = 0.0
            if 'stock.landed.cost' in self.env:
                # نبحث فقط في الفواتير المؤكدة
                valid_invoices = order.invoice_ids.filtered(lambda inv: inv.state == 'posted')
                for invoice in valid_invoices:
                    landed_costs = self.env['stock.landed.cost'].search([
                        ('vendor_bill_id', '=', invoice.id),
                        ('state', '=', 'done')  # فقط التكاليف المكتملة
                    ])
                    if landed_costs:
                        total += sum(landed_costs.mapped('amount_total'))
            order.landed_cost_total = total or 0.0  # تأكد من عدم إرجاع قيمة فارغة

    @api.depends('amount_total', 'currency_id')
    def _compute_total_in_sar(self):
        for order in self:
            company_currency = order.company_currency_id
            if order.currency_id != company_currency:
                order.total_in_sar = order.currency_id._convert(
                    order.amount_total, company_currency,
                    order.company_id, order.date_order or fields.Date.today()
                )
            else:
                order.total_in_sar = order.amount_total

    @api.depends('amount_total', 'landed_cost_total', 'currency_id')
    def _compute_total_supplier_cost(self):
        for order in self:
            company_currency = order.company_currency_id
            if order.currency_id != company_currency:
                total_in_sar = order.currency_id._convert(
                    order.amount_total, company_currency,
                    order.company_id, order.date_order or fields.Date.today()
                )
            else:
                total_in_sar = order.amount_total

            order.total_supplier_cost = total_in_sar + order.landed_cost_total
