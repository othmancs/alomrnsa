# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class ReportPartnerLedger(models.AbstractModel):
    _name = 'report.accounting_pdf_reports.report_partnerledger'
    _description = 'Partner Ledger Report'

    def _lines(self, data, partner):
        full_account = []
        currency = self.env['res.currency']
        query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        reconcile_clause = "" if data['form'].get('reconciled', False) else ' AND "account_move_line".full_reconcile_id IS NULL '
        
        if not data.get('computed') or not data['computed'].get('move_state') or not data['computed'].get('account_ids'):
            raise UserError(_('Missing computed data for the report.'))
        
        params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        
        query_opening_balance = """
            SELECT COALESCE(SUM("account_move_line".debit - "account_move_line".credit), 0)
            FROM """ + query_get_data[0] + """
            LEFT JOIN account_move m ON (m.id="account_move_line".move_id)
            WHERE "account_move_line".partner_id = %s
                AND "account_move_line".account_id IN %s
                AND "account_move_line".date < %s
                AND m.state IN %s """ + reconcile_clause
        
        self.env.cr.execute(query_opening_balance, (partner.id, tuple(data['computed']['account_ids']), data['form']['date_from'], tuple(data['computed']['move_state'])))
        opening_balance = self.env.cr.fetchone()[0] or 0.0
        
        sum = opening_balance
        
        query = """
            SELECT "account_move_line".id, "account_move_line".date, j.code, acc.code as a_code, 
                acc.name as a_name, "account_move_line".ref, m.name as move_name, 
                "account_move_line".name, "account_move_line".debit, "account_move_line".credit, 
                "account_move_line".amount_currency, "account_move_line".currency_id, 
                c.symbol AS currency_code
            FROM """ + query_get_data[0] + """
            LEFT JOIN account_journal j ON ("account_move_line".journal_id = j.id)
            LEFT JOIN account_account acc ON ("account_move_line".account_id = acc.id)
            LEFT JOIN res_currency c ON ("account_move_line".currency_id=c.id)
            LEFT JOIN account_move m ON (m.id="account_move_line".move_id)
            WHERE "account_move_line".partner_id = %s
                AND m.state IN %s
                AND "account_move_line".account_id IN %s AND """ + query_get_data[1] + reconcile_clause + """
            ORDER BY "account_move_line".date"""
        
        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()
        
        if not res:
            full_account.append({
                'date': data['form']['date_from'],
                'displayed_name': _('Opening Balance'),
                'debit': 0.0,
                'credit': 0.0,
                'progress': sum,
                'currency_id': False,
            })
        
        for r in res:
            r['displayed_name'] = '-'.join(
                r[field_name] for field_name in ('move_name', 'ref', 'name')
                if r[field_name] not in (None, '', '/')
            )
            sum += r['debit'] - r['credit']
            r['progress'] = sum
            r['currency_id'] = currency.browse(r.get('currency_id'))
            full_account.append(r)
        
        return full_account

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data or not data.get('form'):
            raise UserError(_('Form content is missing, this report cannot be printed.'))
        
        data['computed'] = {}
        obj_partner = self.env['res.partner']
        query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        data['computed']['move_state'] = ['draft', 'posted'] if data['form'].get('target_move', 'all') == 'all' else ['posted']
        
        self.env.cr.execute("""
            SELECT a.id
            FROM account_account a
            WHERE a.account_type IN %s
            AND NOT a.deprecated""", (tuple(['asset_receivable', 'liability_payable']),))
        data['computed']['account_ids'] = [a for (a,) in self.env.cr.fetchall()]
        
        self.env.cr.execute("""
            SELECT DISTINCT "account_move_line".partner_id
            FROM """ + query_get_data[0] + ", account_move AS am
            WHERE "account_move_line".partner_id IS NOT NULL
                AND am.id = "account_move_line".move_id
                AND am.state IN %s
                AND "account_move_line".account_id IN %s
                AND """ + query_get_data[1], (tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])))
        
        partner_ids = [res['partner_id'] for res in self.env.cr.dictfetchall()]
        partners = obj_partner.browse(partner_ids)
        
        return {
            'doc_ids': partner_ids,
            'doc_model': 'res.partner',
            'data': data,
            'docs': partners,
            'time': time,
            'lines': self._lines,
        }










# # -*- coding: utf-8 -*-

# import time
# from odoo import api, models, _
# from odoo.exceptions import UserError


# class ReportPartnerLedger(models.AbstractModel):
#     _name = 'report.accounting_pdf_reports.report_partnerledger'
#     _description = 'Partner Ledger Report'

#     # def _lines(self, data, partner):
#     #     full_account = []
#     #     currency = self.env['res.currency']
#     #     query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
#     #     reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '
#     #     params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
#     #     query = """
#     #         SELECT "account_move_line".id, "account_move_line".date, j.code, acc.code as a_code, acc.name as a_name, "account_move_line".ref, m.name as move_name, "account_move_line".name, "account_move_line".debit, "account_move_line".credit, "account_move_line".amount_currency,"account_move_line".currency_id, c.symbol AS currency_code
#     #         FROM """ + query_get_data[0] + """
#     #         LEFT JOIN account_journal j ON ("account_move_line".journal_id = j.id)
#     #         LEFT JOIN account_account acc ON ("account_move_line".account_id = acc.id)
#     #         LEFT JOIN res_currency c ON ("account_move_line".currency_id=c.id)
#     #         LEFT JOIN account_move m ON (m.id="account_move_line".move_id)
#     #         WHERE "account_move_line".partner_id = %s
#     #             AND m.state IN %s
#     #             AND "account_move_line".account_id IN %s AND """ + query_get_data[1] + reconcile_clause + """
#     #             ORDER BY "account_move_line".date"""
#     #     self.env.cr.execute(query, tuple(params))
#     #     res = self.env.cr.dictfetchall()
#     #     sum = 0.0
#     #     lang_code = self.env.context.get('lang') or 'en_US'
#     #     lang = self.env['res.lang']
#     #     lang_id = lang._lang_get(lang_code)
#     #     date_format = lang_id.date_format
#     #     for r in res:
#     #         r['date'] = r['date']
#     #         r['displayed_name'] = '-'.join(
#     #             r[field_name] for field_name in ('move_name', 'ref', 'name')
#     #             if r[field_name] not in (None, '', '/')
#     #         )
#     #         sum += r['debit'] - r['credit']
#     #         r['progress'] = sum
#     #         r['currency_id'] = currency.browse(r.get('currency_id'))
#     #         full_account.append(r)
#     #     return full_account
# def _lines(self, data, partner):
#     full_account = []
#     currency = self.env['res.currency']
#     query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
#     reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '
#     params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
    
#     # استعلام لجلب الرصيد الافتتاحي قبل التاريخ المحدد
#     query_opening_balance = """
#         SELECT COALESCE(SUM("account_move_line".debit - "account_move_line".credit), 0)
#         FROM """ + query_get_data[0] + """
#         LEFT JOIN account_move m ON (m.id="account_move_line".move_id)
#         WHERE "account_move_line".partner_id = %s
#             AND "account_move_line".account_id IN %s
#             AND "account_move_line".date < %s
#             AND m.state IN %s """ + reconcile_clause
    
#     self.env.cr.execute(query_opening_balance, (partner.id, tuple(data['computed']['account_ids']), data['form']['date_from'], tuple(data['computed']['move_state'])))
#     opening_balance = self.env.cr.fetchone()[0] or 0.0
    
#     sum = opening_balance  # بدء التراكمي من الرصيد الافتتاحي
    
#     query = """
#         SELECT "account_move_line".id, "account_move_line".date, j.code, acc.code as a_code, 
#                acc.name as a_name, "account_move_line".ref, m.name as move_name, 
#                "account_move_line".name, "account_move_line".debit, "account_move_line".credit, 
#                "account_move_line".amount_currency, "account_move_line".currency_id, 
#                c.symbol AS currency_code
#         FROM """ + query_get_data[0] + """
#         LEFT JOIN account_journal j ON ("account_move_line".journal_id = j.id)
#         LEFT JOIN account_account acc ON ("account_move_line".account_id = acc.id)
#         LEFT JOIN res_currency c ON ("account_move_line".currency_id=c.id)
#         LEFT JOIN account_move m ON (m.id="account_move_line".move_id)
#         WHERE "account_move_line".partner_id = %s
#             AND m.state IN %s
#             AND "account_move_line".account_id IN %s AND """ + query_get_data[1] + reconcile_clause + """
#         ORDER BY "account_move_line".date"""


#     self.env.cr.execute(query, tuple(params))
#     res = self.env.cr.dictfetchall()
    
#     # إضافة الرصيد الافتتاحي إذا لم تكن هناك حركات
#     if not res:
#         full_account.append({
#             'date': data['form']['date_from'],
#             'displayed_name': _('Opening Balance'),
#             'debit': 0.0,
#             'credit': 0.0,
#             'progress': sum,
#             'currency_id': False,
#         })
    
#     for r in res:
#         r['date'] = r['date']
#         r['displayed_name'] = '-'.join(
#             r[field_name] for field_name in ('move_name', 'ref', 'name')
#             if r[field_name] not in (None, '', '/')
#         )
#         sum += r['debit'] - r['credit']
#         r['progress'] = sum
#         r['currency_id'] = currency.browse(r.get('currency_id'))
#         full_account.append(r)
    
#     return full_account
#     def _sum_partner(self, data, partner, field):
#         if field not in ['debit', 'credit', 'debit - credit']:
#             return
#         result = 0.0
#         query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
#         reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '

#         params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
#         query = """SELECT sum(""" + field + """)
#                 FROM """ + query_get_data[0] + """, account_move AS m
#                 WHERE "account_move_line".partner_id = %s
#                     AND m.id = "account_move_line".move_id
#                     AND m.state IN %s
#                     AND account_id IN %s
#                     AND """ + query_get_data[1] + reconcile_clause
#         self.env.cr.execute(query, tuple(params))

#         contemp = self.env.cr.fetchone()
#         if contemp is not None:
#             result = contemp[0] or 0.0
#         return result

#     @api.model
#     def _get_report_values(self, docids, data=None):
#         if not data.get('form'):
#             raise UserError(_("Form content is missing, this report cannot be printed."))
#         data['computed'] = {}

#         obj_partner = self.env['res.partner']
#         query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
#         data['computed']['move_state'] = ['draft', 'posted']
#         if data['form'].get('target_move', 'all') == 'posted':
#             data['computed']['move_state'] = ['posted']
#         result_selection = data['form'].get('result_selection', 'customer')
#         if result_selection == 'supplier':
#             data['computed']['ACCOUNT_TYPE'] = ['liability_payable']
#         elif result_selection == 'customer':
#             data['computed']['ACCOUNT_TYPE'] = ['asset_receivable']
#         else:
#             data['computed']['ACCOUNT_TYPE'] = ['asset_receivable', 'liability_payable']

#         self.env.cr.execute("""
#             SELECT a.id
#             FROM account_account a
#             WHERE a.account_type IN %s
#             AND NOT a.deprecated""", (tuple(data['computed']['ACCOUNT_TYPE']),))
#         data['computed']['account_ids'] = [a for (a,) in self.env.cr.fetchall()]
#         params = [tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
#         reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '
#         query = """
#             SELECT DISTINCT "account_move_line".partner_id
#             FROM """ + query_get_data[0] + """, account_account AS account, account_move AS am
#             WHERE "account_move_line".partner_id IS NOT NULL
#                 AND "account_move_line".account_id = account.id
#                 AND am.id = "account_move_line".move_id
#                 AND am.state IN %s
#                 AND "account_move_line".account_id IN %s
#                 AND NOT account.deprecated
#                 AND """ + query_get_data[1] + reconcile_clause
#         self.env.cr.execute(query, tuple(params))
#         if data['form']['partner_ids']:
#             partner_ids = data['form']['partner_ids']
#         else:
#             partner_ids = [res['partner_id'] for res in
#                            self.env.cr.dictfetchall()]
#         partners = obj_partner.browse(partner_ids)
#         partners = sorted(partners, key=lambda x: (x.ref or '', x.name or ''))

#         return {
#             'doc_ids': partner_ids,
#             'doc_model': self.env['res.partner'],
#             'data': data,
#             'docs': partners,
#             'time': time,
#             'lines': self._lines,
#             'sum_partner': self._sum_partner,
#         }
