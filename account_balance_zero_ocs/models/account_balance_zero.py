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
        """حساب الرصيد بطريقة آمنة"""
        self.env.cr.execute("""
            SELECT SUM(balance) as balance
            FROM account_move_line
            WHERE account_id = %s
              AND date <= %s
              AND parent_state = 'posted'
        """, (account_id, self.date))
        result = self.env.cr.fetchone()
        return result[0] or 0.0

    def _prepare_move_data(self):
        """إعداد بيانات القيد مع التحقق من الحسابات المسموح بها"""
        accounts = self.env['account.account'].search([('deprecated', '=', False)])
        move_lines = []
        restricted_accounts = []

        for account in accounts:
            if account.allowed_journal_ids and self.journal_id not in account.allowed_journal_ids:
                restricted_accounts.append(account.name)
                continue

            balance = self._compute_account_balance(account.id)
            if balance:
                amount = abs(balance)
                move_lines.append((0, 0, {
                    'account_id': account.id,
                    'debit': balance > 0 and amount or 0.0,
                    'credit': balance < 0 and amount or 0.0,
                    'name': _('تصفير رصيد الإغلاق'),
                }))

        warning_message = ''
        if restricted_accounts:
            warning_message = _("""
                تم استبعاد الحسابات التالية لأنها غير مسموح بها في دفتر اليومية المحدد:
                %s
                سيتم المتابعة مع الحسابات المسموح بها.
            """) % '\n'.join(restricted_accounts)

        return {
            'move_lines': move_lines,
            'warning_message': warning_message,
            'has_warning': bool(restricted_accounts)
        }

    def action_zero_balances(self):
        """البدء في العملية"""
        self.ensure_one()
        move_data = self._prepare_move_data()

        if not move_data['move_lines']:
            raise UserError(_("لا توجد أرصدة لتصفيرها في التاريخ المحدد"))

        if move_data['has_warning']:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('تحذير'),
                    'message': move_data['warning_message'],
                    'type': 'warning',
                    'sticky': False,
                    'next': {
                        'type': 'ir.actions.act_window',
                        'res_model': 'account.move',
                        'view_mode': 'form',
                        'res_id': self._create_move(move_data['move_lines']).id,
                    }
                }
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': self._create_move(move_data['move_lines']).id,
            }

    def _create_move(self, move_lines):
        """إنشاء القيد المحاسبي"""
        move = self.env['account.move'].create({
            'date': self.date,
            'journal_id': self.journal_id.id,
            'ref': self.ref,
            'line_ids': move_lines,
        })
        move.action_post()
        return move
