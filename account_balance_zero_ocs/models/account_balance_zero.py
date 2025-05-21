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
    
    # هذه الحقول يجب أن تكون غير مخزنة (transient) لأنها للاستخدام المؤقت فقط
    show_warning = fields.Boolean(compute='_compute_warning_fields', store=False)
    warning_message = fields.Text(compute='_compute_warning_fields', store=False)
    restricted_accounts = fields.Text(compute='_compute_warning_fields', store=False)

    @api.depends('date', 'journal_id')
    def _compute_warning_fields(self):
        """حساب الحقول المحسوبة بشكل ديناميكي"""
        for record in self:
            record.show_warning = False
            record.warning_message = ''
            record.restricted_accounts = ''

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

        # تخزين بيانات التحذير في الحقول المحسوبة
        if restricted_accounts:
            self.update({
                'show_warning': True,
                'warning_message': _("""
                    تم استبعاد الحسابات التالية لأنها غير مسموح بها في دفتر اليومية المحدد:
                    %s
                    سيتم المتابعة مع الحسابات المسموح بها.
                """) % '\n'.join(restricted_accounts),
                'restricted_accounts': '\n'.join(restricted_accounts)
            })

        return {
            'date': self.date,
            'journal_id': self.journal_id.id,
            'ref': self.ref,
            'line_ids': move_lines,
        }

    def action_show_warning(self):
        """عرض التحذير ثم المتابعة"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('تحذير'),
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'views': [(False, 'form')],
        }

    def action_create_move(self):
        """إنشاء القيد المحاسبي"""
        move_data = self._prepare_move_data()

        if not move_data['line_ids']:
            raise UserError(_("لا توجد أرصدة لتصفيرها في التاريخ المحدد"))

        move = self.env['account.move'].create(move_data)
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
        move_data = self._prepare_move_data()

        if self.show_warning:
            return self.action_show_warning()
        return self.action_create_move()
