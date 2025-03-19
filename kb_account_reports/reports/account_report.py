# -*- coding: utf-8 -*-


import pytz
import time
from operator import itemgetter
from itertools import groupby
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, date


class KBAccountReport(models.AbstractModel):
    _name = 'report.kb_account_reports.account_report'
    _description = "Report Account"

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('kb_account_reports.account_report_template.xml')
        domain = [('date', '<=', data['end_date']), ('date', '>=', data['start_date']), ('account_id', '=', data['account_id'])]
        if data['state'] == 'draft':
            state = 'Unposted'
            domain.append(('parent_state', '=', 'draft'))
        elif data['state'] == 'posted':
            state = 'Posted'
            domain.append(('parent_state', '=', 'posted'))
        else:
            state = 'All'
        move_line_ids = self.env['account.move.line'].search(domain, order='date asc, move_id DESC')
        
        domain = [ ('date', '<', data['start_date']), ('account_id', '=', data['account_id'])]
        if data['state'] == 'draft':
            state = 'Unposted'
            domain.append(('parent_state', '=', 'draft'))
        elif data['state'] == 'posted':
            state = 'Posted'
            domain.append(('parent_state', '=', 'posted'))
        else:
            state = 'All'
        move_balance = self.env['account.move.line'].search(domain)
        
        return {
           'doc_model': report.model,
           'lines': move_line_ids,
           'move_balance':move_balance,
           'start_date': data['start_date'],
           'end_date': data['end_date'],
           'state': state,
           'account_id': data['account_id']
        }
