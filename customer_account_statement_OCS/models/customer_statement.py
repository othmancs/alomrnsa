from odoo import models, fields, api
from datetime import datetime

class PartnerStatementReport(models.AbstractModel):
    _name = 'report.customer_account_statement_OCS.report_customer_statement_template'
    
    def _get_report_values(self, docids, data=None):
        partner = self.env['res.partner'].browse(docids)
        
        # جلب بيانات الحركات المالية
        moves = self.env['account.move.line'].search([
            ('partner_id', '=', partner.id),
            ('date', '>=', data.get('date_from')),
            ('date', '<=', data.get('date_to')),
        ], order='date asc')
        
        # حساب الرصيد الافتتاحي والختامي
        initial_balance = sum(moves.mapped('debit')) - sum(moves.mapped('credit'))
        closing_balance = initial_balance
        
        # تحضير بيانات الحركات
        lines = []
        for move in moves:
            lines.append({
                'date': move.date,
                'move_name': move.move_id.name,
                'name': move.name,
                'debit': move.debit,
                'credit': move.credit,
                'balance': move.balance,
                'reference': move.ref,
            })
            closing_balance += move.balance
        
        return {
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'docs': partner,
            'data': data,
            'lines': lines,
            'initial_balance': initial_balance,
            'closing_balance': closing_balance,
            'show_initial_balance': True,
            'format_amount': self._format_amount,
            'datetime': datetime,
        }
    
    def _format_amount(self, amount, currency):
        return "{:,.2f} {}".format(amount or 0.0, currency.symbol if currency else "")
