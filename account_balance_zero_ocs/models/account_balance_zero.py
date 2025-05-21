from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountBalanceZero(models.TransientModel):
    _name = 'account.balance.zero'
    _description = 'تصفير أرصدة الإغلاق'

    date = fields.Date(string='التاريخ', required=True, default=fields.Date.context_today)
    journal_id = fields.Many2one(
        'account.journal',
        string='دفتر اليومية',
        required=True,
        domain=[('type', '=', 'general')]
    )
    ref = fields.Char(string='المرجع', default='تصفير أرصدة الإغلاق')

    def _compute_account_balance(self, account_id):
        """حساب الرصيد بطريقة آمنة تتجنب مشاكل المؤقت"""
        self.env.cr.execute("""
            SELECT SUM(balance) as balance
            FROM account_move_line
            WHERE account_id = %s
              AND date <= %s
              AND parent_state = 'posted'
        """, (account_id, self.date))
        result = self.env.cr.fetchone()
        return result[0] or 0.0

    def action_zero_balances(self):
        self.ensure_one()
        
        Account = self.env['account.account']
        Move = self.env['account.move']
        
        accounts = Account.search([('deprecated', '=', False)])
        
        if not accounts:
            raise UserError(_("لا توجد حسابات متاحة لتصفير الأرصدة"))
        
        move_vals = {
            'date': self.date,
            'journal_id': self.journal_id.id,
            'ref': self.ref,
            'line_ids': [],
        }
        
        restricted_accounts = []
        
        for account in accounts:
            # التحقق من أن الحساب مسموح به في دفتر اليومية المحدد
            if account.allowed_journal_ids and self.journal_id not in account.allowed_journal_ids:
                restricted_accounts.append(account.name)
                continue
            
            balance = self._compute_account_balance(account.id)
            
            if balance:
                amount = abs(balance)
                debit = balance > 0 and amount or 0.0
                credit = balance < 0 and amount or 0.0
                
                move_vals['line_ids'].append((0, 0, {
                    'account_id': account.id,
                    'debit': debit,
                    'credit': credit,
                    'name': _('تصفير رصيد الإغلاق'),
                }))
        
        if restricted_accounts:
            warning_msg = _("""
                تم استبعاد الحسابات التالية لأنها غير مسموح بها في دفتر اليومية المحدد:
                %s
            """) % '\n'.join(restricted_accounts)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('تحذير'),
                    'message': warning_msg,
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        if move_vals['line_ids']:
            move = Move.create(move_vals)
            move.action_post()
            return {
                'name': _('قيد تصفير الأرصدة'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id': move.id,
            }
        else:
            raise UserError(_("لا توجد أرصدة لتصفيرها في التاريخ المحدد"))
