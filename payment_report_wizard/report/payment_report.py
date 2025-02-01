from odoo import models

class PaymentReport(models.AbstractModel):
    _name = 'report.payment_report_wizard.payment_report_template'
    _description = 'Payment Report'

    def _get_report_values(self, docids, data=None):
        docs = self.env['account.payment'].search([
            ('date', '>=', data.get('date_from')),
            ('date', '<=', data.get('date_to')),
        ])
        return {
            'doc_ids': docids,
            'doc_model': 'account.payment',
            'docs': docs,
        }
