from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class CustomerStatementReport(models.AbstractModel):
    _name = 'report.customer_statement.customer_statement_template'
    _description = 'Customer Statement Report'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('partner_id'):
            raise UserError(_("Please select a customer."))
            
        partner = self.env['res.partner'].browse(data['partner_id'])
        date_from = data['date_from']
        date_to = data['date_to']
        branch_id = data.get('branch_id', False)
        
        # حساب الرصيد الافتتاحي
        domain = [
            ('partner_id', '=', partner.id),
            ('date', '<', date_from),
            ('move_id.state', '=', 'posted'),
            ('account_id.account_type', 'in', ['receivable', 'payable']),
        ]
        if branch_id:
            domain.append(('branch_id', '=', branch_id))
            
        opening_lines = self.env['account.move.line'].search(domain)
        opening_debit = sum(opening_lines.mapped('debit'))
        opening_credit = sum(opening_lines.mapped('credit'))
        opening_balance = opening_debit - opening_credit
        
        # جلب حركات الفترة
        domain = [
            ('partner_id', '=', partner.id),
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('move_id.state', '=', 'posted'),
            ('account_id.account_type', 'in', ['receivable', 'payable']),
        ]
        if branch_id:
            domain.append(('branch_id', '=', branch_id))
            
        period_lines = self.env['account.move.line'].search(domain, order='date, move_id')
        
        # حساب المجاميع خلال الفترة
        period_debit = sum(period_lines.mapped('debit'))
        period_credit = sum(period_lines.mapped('credit'))
        period_balance = period_debit - period_credit
        
        # حساب الرصيد الختامي
        closing_balance = opening_balance + period_balance
        
        # تحضير بيانات الأسطر
        lines = []
        running_balance = opening_balance
        for line in period_lines:
            running_balance += line.debit - line.credit
            lines.append({
                'date': line.date,
                'move_name': line.move_id.name,
                'ref': line.ref or '',
                'debit': line.debit,
                'credit': line.credit,
                'balance': running_balance,
            })
        
        return {
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'partner': partner,
            'date_from': date_from,
            'date_to': date_to,
            'branch': self.env['multi.branch'].browse(branch_id) if branch_id else False,
            'opening_balance': opening_balance,
            'opening_debit': opening_debit,
            'opening_credit': opening_credit,
            'period_debit': period_debit,
            'period_credit': period_credit,
            'period_balance': period_balance,
            'closing_balance': closing_balance,
            'lines': lines,
        }
