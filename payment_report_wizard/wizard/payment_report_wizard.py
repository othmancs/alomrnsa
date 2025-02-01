from odoo import models, fields, api

class PaymentReportWizard(models.TransientModel):
    _name = 'payment.report.wizard'
    _description = 'Payment Report Wizard'

    date_from = fields.Date(string="Date From", required=True)
    date_to = fields.Date(string="Date To", required=True)
    journal_id = fields.Many2one('account.journal', string="Journal")
    branch_id = fields.Many2one('res.partner', string="Branch")

    def action_print_report(self):
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'journal_id': self.journal_id.id,
            'branch_id': self.branch_id.id,
        }
        return self.env.ref('payment_report_wizard.action_payment_report').report_action(self, data=data)
