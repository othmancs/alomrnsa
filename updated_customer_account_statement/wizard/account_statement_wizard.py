
from odoo import models, fields, api

class AccountStatementWizard(models.TransientModel):
    _name = 'account.statement.wizard'
    _description = 'Wizard for Customer Account Statement'

    partner_id = fields.Many2one('res.partner', string='العميل', required=True, domain=[('customer_rank', '>', 0)])
    date_from = fields.Date(string='من تاريخ', required=True)
    date_to = fields.Date(string='إلى تاريخ', required=True)
    export_type = fields.Selection([
        ('pdf', 'PDF'),
        ('xlsx', 'Excel')
    ], string="نوع التقرير", default="pdf", required=True)

    def generate_report(self):
        data = {
            'partner_id': self.partner_id.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
        }
        if self.export_type == 'pdf':
            return self.env.ref('customer_account_statement.customer_account_statement_pdf').report_action(self, data=data)
        else:
            return self.env.ref('customer_account_statement.customer_account_statement_xlsx').report_action(self, data=data)
