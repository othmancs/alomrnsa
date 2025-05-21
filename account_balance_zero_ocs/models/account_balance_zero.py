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
    show_warning = fields.Boolean(default=False)
    warning_message = fields.Text()

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

    def _prepare_move_lines(self):
        """إعداد بنود القيد مع التحقق من الحسابات المسموح بها"""
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

        if restricted_accounts:
            self.warning_message = _("""
                تم استبعاد الحسابات التالية لأنها غير مسموح بها في دفتر اليومية المحدد:
                %s
                سيتم المتابعة مع الحسابات المسموح بها.
            """) % '\n'.join(restricted_accounts)
            self.show_warning = True

        return move_lines

    def action_show_warning(self):
        """عرض التحذير ثم المتابعة"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('تحذير'),
            'res_model': 'account.balance.zero',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_continue(self):
        """المتابعة بعد التحذير"""
        self.ensure_one()
        return self.action_create_move()

    def action_create_move(self):
        """إنشاء القيد المحاسبي"""
        move_lines = self._prepare_move_lines()

        if not move_lines:
            raise UserError(_("لا توجد أرصدة لتصفيرها في التاريخ المحدد"))

        move = self.env['account.move'].create({
            'date': self.date,
            'journal_id': self.journal_id.id,
            'ref': self.ref,
            'line_ids': move_lines,
        })
        move.action_post()

        return {
            'name': _('قيد تصفير الأرصدة'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': move.id,
            'context': {'create': False},
        }

    def action_zero_balances(self):
        """البدء في العملية"""
        self.ensure_one()
        move_lines = self._prepare_move_lines()

        if self.show_warning:
            return self.action_show_warning()
        else:
            return self.action_create_move()
