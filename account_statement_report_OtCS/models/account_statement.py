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
        return self.env.ref('account_statement_report.action_account_statement').report_action(self)

    def _get_statement_lines(self):
        self.ensure_one()
        domain = [
            ('partner_id', '=', self.partner_id.id),
            ('company_id', '=', self.company_id.id),
            ('reconciled', '=', False),
        ]

        if self.date_from:
            domain.append(('date', '>=', self.date_from))
        if self.date_to:
            domain.append(('date', '<=', self.date_to))

        move_lines = self.env['account.move.line'].search(domain, order='date, id')

        lines = []
        for line in move_lines:
            lines.append({
                'date': line.date,
                'name': line.name or line.move_id.name,
                'ref': line.ref or line.move_id.ref,
                'debit': line.debit,
                'credit': line.credit,
            })

        return lines