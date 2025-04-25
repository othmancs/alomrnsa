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

    @api.depends('invoice_ids', 'order_line.invoice_lines.move_id')
    def _compute_landed_cost_total(self):
        for order in self:
            total = 0.0
            if 'stock.landed.cost' in self.env:
                # الحصول على جميع فواتير المورد المرتبطة
                vendor_bills = order.invoice_ids.filtered(
                    lambda inv: inv.move_type == 'in_invoice' and inv.state == 'posted'
                )
                
                # بديل إضافي للحصول على الفواتير
                if not vendor_bills:
                    vendor_bills = order.order_line.invoice_lines.move_id.filtered(
                        lambda inv: inv.move_type == 'in_invoice' and inv.state == 'posted'
                    )
                
                if vendor_bills:
                    # البحث بكافة الطرق الممكنة
                    landed_costs = self.env['stock.landed.cost'].search([
                        '|',
                        ('vendor_bill_id', 'in', vendor_bills.ids),
                        ('invoice_id', 'in', vendor_bills.ids),
                        '|',
                        ('picking_ids', 'in', order.picking_ids.ids),
                        ('purchase_ids', 'in', order.ids)
                    ])
                    
                    # تسجيل تفاصيل التصحيح
                    if not landed_costs:
                        _logger.warning(f"لم يتم العثور على تكاليف شحن للطلب {order.name} والفواتير {vendor_bills.mapped('name')}")
                    else:
                        _logger.info(f"تم العثور على {len(landed_costs)} تكلفة شحن للطلب {order.name}")
                        for cost in landed_costs:
                            _logger.info(f"التكلفة: {cost.name} - المبلغ: {cost.amount_total} - الفاتورة: {cost.invoice_id.name or cost.vendor_bill_id.name}")
                    
                    total = sum(landed_costs.mapped('amount_total'))
            
            order.landed_cost_total = total
      
    @api.depends('amount_total', 'currency_id')
    def _compute_total_in_sar(self):
        for order in self:
            company_currency = order.company_currency_id
            if order.currency_id and company_currency and order.currency_id != company_currency:
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
            if order.currency_id and company_currency and order.currency_id != company_currency:
                total_in_sar = order.currency_id._convert(
                    order.amount_total, company_currency,
                    order.company_id, order.date_order or fields.Date.today()
                )
            else:
                total_in_sar = order.amount_total

            order.total_supplier_cost = total_in_sar + order.landed_cost_total
