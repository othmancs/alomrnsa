from odoo import models, fields, api

class DailySalesReportWizard(models.TransientModel):
    _name = 'daily.sales.report.wizard'
    _description = 'تقرير المبيعات اليومية - ويزرد'

    date_from = fields.Date(string='من تاريخ', required=True, default=fields.Date.context_today)
    date_to = fields.Date(string='إلى تاريخ', required=True, default=fields.Date.context_today)
    branch_id = fields.Many2one('res.branch', string='الفرع')

    def generate_report(self):
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'branch_id': self.branch_id.id,
            'branch_name': self.branch_id.name or 'الكل'
        }
        # ✅ تم تعديل الـ xml_id ليطابق اسم الموديول الصحيح
        return self.env.ref('sales_reports_othman.daily_sales_report_action').report_action(self, data=data)


class DailySalesReport(models.AbstractModel):
    _name = 'report.sales_reports_othman.daily_sales_report_template'
    _description = 'تقرير المبيعات اليومية'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = data['date_from']
        date_to = data['date_to']
        branch_id = data['branch_id']

        domain = [
            ('date_order', '>=', date_from),
            ('date_order', '<=', date_to),
            ('state', 'in', ['sale', 'done'])
        ]
        
        if branch_id:
            domain.append(('branch_id', '=', branch_id))

        orders = self.env['sale.order'].search(domain)
        
        # حساب المبيعات النقدية
        cash_sales = sum(orders.filtered(
            lambda o: o.payment_term_id.is_cash and o.invoice_status == 'invoiced' and 
            all(inv.payment_state == 'paid' for inv in o.invoice_ids)
        ).mapped('amount_total')) or 0.0

        # حساب المبيعات الآجلة
        credit_sales = sum(orders.filtered(
            lambda o: not o.payment_term_id.is_cash and o.invoice_status == 'invoiced' and 
            any(inv.payment_state != 'paid' for inv in o.invoice_ids)
        ).mapped('amount_total')) or 0.0

        # المرتجعات النقدية
        cash_returns = sum(self.env['account.move'].search([
            ('move_type', '=', 'out_refund'),
            ('invoice_date', '>=', date_from),
            ('invoice_date', '<=', date_to),
            ('payment_state', '=', 'paid'),
            ('branch_id', '=', branch_id) if branch_id else (1, '=', 1)
        ]).mapped('amount_total_signed')) or 0.0

        # المرتجعات الآجلة
        credit_returns = sum(self.env['account.move'].search([
            ('move_type', '=', 'out_refund'),
            ('invoice_date', '>=', date_from),
            ('invoice_date', '<=', date_to),
            ('payment_state', '!=', 'paid'),
            ('branch_id', '=', branch_id) if branch_id else (1, '=', 1)
        ]).mapped('amount_total_signed')) or 0.0

        # المدفوعات النقدية
        cash_payments = sum(self.env['account.payment'].search([
            ('payment_type', '=', 'inbound'),
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('branch_id', '=', branch_id) if branch_id else (1, '=', 1)
        ]).mapped('amount')) or 0.0

        # الفواتير الآجلة
        credit_invoices = sum(self.env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('invoice_date', '>=', date_from),
            ('invoice_date', '<=', date_to),
            ('payment_state', '!=', 'paid'),
            ('branch_id', '=', branch_id) if branch_id else (1, '=', 1)
        ]).mapped('amount_total_signed')) or 0.0

        total_sales = cash_sales + credit_sales
        total_returns = cash_returns + credit_returns

        return {
            'doc_ids': orders.ids,
            'doc_model': 'sale.order',
            'date_from': date_from,
            'date_to': date_to,
            'branch_name': data['branch_name'],
            'cash_sales': cash_sales,
            'credit_sales': credit_sales,
            'cash_returns': abs(cash_returns),
            'credit_returns': abs(credit_returns),
            'cash_payments': cash_payments,
            'credit_invoices': credit_invoices,
            'total_sales': total_sales,
            'total_returns': total_returns,
            'net_sales': total_sales - total_returns,
        }
