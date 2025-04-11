from odoo import models, fields, api


class CustomerStatementWizard(models.TransientModel):
    _name = 'customer.statement.wizard'
    _description = 'Customer Statement Wizard'

    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        domain=[('customer_rank', '>', 0)]
    )
    date_from = fields.Date(string='From Date', required=True)
    date_to = fields.Date(string='To Date', required=True, default=fields.Date.today)
    show_initial_balance = fields.Boolean(string='Show Initial Balance', default=True)
    show_invoice_details = fields.Boolean(string='Show Invoice Details', default=False)

    def action_print_statement(self):
        data = {
            'partner_id': self.partner_id.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'show_initial_balance': self.show_initial_balance,
            'show_invoice_details': self.show_invoice_details,
        }
        return self.env.ref('customer_statement.action_customer_statement_report').report_action(self, data=data)