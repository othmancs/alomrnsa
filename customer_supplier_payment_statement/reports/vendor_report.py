import pytz
import time
from operator import itemgetter
from itertools import groupby
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, date


class KBAccountReport(models.AbstractModel):
    _name = 'report.customer_payment_statement.vendor_statement_report'
    _description = "Vendor Statement report"

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('customer_vendor_statement.action_customer_template.xml')
        domain = [('invoice_date', '<=', data['end_date']), ('invoice_date', '>=', data['start_date']),
                  ('partner_id', '=', data['partner_id'])]

        moves = self.env['account.move'].search(domain)
        partner = self.env['res.partner'].search([('id', '=',  data['partner_id'])])
        return {
            'doc_model': report.model,
            'move_details': moves,
            'partner_id': partner,
            'start_date': data['start_date'],
            'end_date': data['end_date'],
        }