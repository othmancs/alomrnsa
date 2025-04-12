from odoo import models, fields, api

class AccountStatementWizard(models.TransientModel):
    _name = 'account.statement.wizard'
    _description = 'Account Statement Wizard'

    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    date_from = fields.Date(string='From Date')
    date_to = fields.Date(string='To Date', default=fields.Date.context_today)
    show_details = fields.Boolean(string='Show Detailed Moves', default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    def action_print_statement(self):
        # تأكد من أن التقرير موجود أولاً
        report = self.env.ref('account_statement_report.action_account_statement', raise_if_not_found=False)
        
        if not report:
            # إنشاء التقرير ديناميكياً إذا لم يوجد
            return {
                'type': 'ir.actions.report',
                'report_name': 'account_statement_report.account_statement_template',
                'model': 'account.statement.wizard',
                'report_type': 'qweb-html',
                'context': dict(self.env.context, active_model='account.statement.wizard'),
            }
        return report.report_action(self)


    def _get_statement_lines(self):
        self.ensure_one()
        AccountMoveLine = self.env['account.move.line']
        
        domain = [
            ('partner_id', '=', self.partner_id.id),
            ('company_id', '=', self.company_id.id),
            ('reconciled', '=', False),
            ('parent_state', '=', 'posted'),  # تضمين فقط الحركات المؤكدة
        ]
    
        if self.date_from:
            domain.append(('date', '>=', self.date_from))
        if self.date_to:
            domain.append(('date', '<=', self.date_to))
    
        fields = ['date', 'name', 'ref', 'debit', 'credit', 'move_id', 'account_id']
        move_lines = AccountMoveLine.search_read(domain, fields, order='date, id')
    
        currency = self.company_id.currency_id
        lines = []
        for line in move_lines:
            lines.append({
                'date': line['date'],
                'name': line['name'] or line['move_id'][1],
                'ref': line['ref'] or line['move_id'][1],
                'debit': line['debit'],
                'credit': line['credit'],
                'account_code': line['account_id'][1] if line['account_id'] else '',
                'currency': currency,
            })
        
        return lines
