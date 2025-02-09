from odoo import models, fields, api

class CustomerStatementWizard(models.TransientModel):
    _name = 'customer.statement.wizard'
    _description = 'Customer Statement Wizard'

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)

    def generate_report(self):
        data = {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'partner_id': self.partner_id.id,
        }
        return self.env.ref('customer_statement.action_report_customer_statement').report_action(None, data=data)
