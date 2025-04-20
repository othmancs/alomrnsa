from odoo import models, fields, api

class CustomerStatementWizard(models.TransientModel):
    _name = 'customer.statement.wizard'
    _description = 'Customer Statement Wizard'

    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    date_from = fields.Date(string='From Date', required=True)
    date_to = fields.Date(string='To Date', required=True)
    branch_id = fields.Many2one('multi.branch', string='Branch')
    
    def action_print_report(self):
        self.ensure_one()
        data = {
            'partner_id': self.partner_id.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'branch_id': self.branch_id.id if self.branch_id else False,
        }
        return self.env.ref('customer_statement_OCSS.action_customer_statement_report').report_action(self, data=data)
