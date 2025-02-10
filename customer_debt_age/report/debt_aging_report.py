from odoo import models, api
from datetime import date

class DebtAgingReport(models.AbstractModel):
    _name = 'report.customer_debt_age.debt_aging_report'
    _description = 'Customer Debt Aging Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['res.partner'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'docs': docs,
            'today': date.today(),
        }
