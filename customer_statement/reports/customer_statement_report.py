from odoo import models, api

class CustomerStatementReport(models.AbstractModel):
    _name = 'report.customer_statement.customer_statement_report'
    _description = 'Customer Statement Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        partner_id = self.env['res.partner'].browse(data.get('partner_id'))

        invoices = self.env['account.move'].search([
            ('partner_id', '=', partner_id.id),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('invoice_date', '>=', start_date),
            ('invoice_date', '<=', end_date),
        ])
        payments = self.env['account.payment'].search([
            ('partner_id', '=', partner_id.id),
            ('date', '>=', start_date),
            ('date', '<=', end_date),
        ])

        transactions = []
        balance = 0
        transactions.append({'date': start_date, 'type': 'Opening Balance', 'description': '-', 'amount': '-', 'balance': balance})

        for invoice in invoices:
            balance += invoice.amount_total_signed
            transactions.append({'date': invoice.invoice_date, 'type': 'Invoice', 'description': invoice.name, 'amount': invoice.amount_total_signed, 'balance': balance})

        for payment in payments:
            balance -= payment.amount
            transactions.append({'date': payment.date, 'type': 'Payment', 'description': payment.name, 'amount': -payment.amount, 'balance': balance})

        transactions.append({'date': end_date, 'type': 'Closing Balance', 'description': '-', 'amount': '-', 'balance': balance})

        return {
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'data': data,
            'partner': partner_id,
            'transactions': transactions,
        }
