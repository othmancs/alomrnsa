from odoo import models, fields, api

class CustomerStatementWizard(models.TransientModel):
    _name = 'customer.statement.wizard'
    _description = 'Customer Statement Wizard'

    date_from = fields.Date(string='Start Date', required=True)
    date_to = fields.Date(string='End Date', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)

    def generate_report(self):
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'partner_id': self.partner_id.id,
        }
        return self.env.ref('customer_statement.action_report_customer_statement').report_action(None, data=data)
