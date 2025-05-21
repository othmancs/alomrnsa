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
    branch_id = fields.Many2one(
        'res.branch',
        string='الفرع',
        required=True
    )

    @api.model
    def default_get(self, fields):
        res = super(AccountBalanceZero, self).default_get(fields)
        # الحصول على فرع المستخدم إذا كان الحقل موجوداً
        if hasattr(self.env.user, 'branch_id'):
            res['branch_id'] = self.env.user.branch_id.id
        return res

    def _compute_account_balance(self, account_id):
        """حساب الرصيد بطريقة آمنة مع مراعاة الفرع"""
        query = """
            SELECT SUM(balance) as balance
            FROM account_move_line
            WHERE account_id = %s
              AND date <= %s
              AND parent_state = 'posted'
        """
        params = [account_id, self.date]
        
        if hasattr(self.env['account.move.line'], 'branch_id'):
            query += " AND branch_id = %s"
            params.append(self.branch_id.id)
        
        self.env.cr.execute(query, params)
        result = self.env.cr.fetchone()
        return result[0] or 0.0

    def _prepare_move_data(self):
        """إعداد بيانات القيد مع التحقق من الفروع"""
        accounts = self.env['account.account'].search([('deprecated', '=', False)])
        move_lines = []
        excluded_accounts = []

        for account in accounts:
            # التحقق من أن الحساب مسموح به في دفتر اليومية المحدد
            if account.allowed_journal_ids and self.journal_id not in account.allowed_journal_ids:
                excluded_accounts.append(f"{account.name} (غير مسموح في دفتر اليومية)")
                continue

            # التحقق من أن الحساب ينتمي للفرع المحدد إذا كان الحقل موجوداً
            if hasattr(account, 'branch_id') and account.branch_id and account.branch_id != self.branch_id:
                excluded_accounts.append(f"{account.name} (فرع {account.branch_id.name})")
                continue

            balance = self._compute_account_balance(account.id)
            if balance:
                amount = abs(balance)
                line_vals = {
                    'account_id': account.id,
                    'debit': balance > 0 and amount or 0.0,
                    'credit': balance < 0 and amount or 0.0,
                    'name': _('تصفير رصيد الإغلاق'),
                }
                if hasattr(self.env['account.move.line'], 'branch_id'):
                    line_vals['branch_id'] = self.branch_id.id
                move_lines.append((0, 0, line_vals))

        warning_msg = ''
        if excluded_accounts:
            warning_msg = _("""
                تم استبعاد الحسابات التالية:
                %s
            """) % '\n'.join(excluded_accounts)

        return {
            'move_lines': move_lines,
            'warning_message': warning_msg,
            'has_warning': bool(excluded_accounts)
        }

    def action_zero_balances(self):
        """البدء في العملية"""
        self.ensure_one()
        move_data = self._prepare_move_data()

        if not move_data['move_lines']:
            raise UserError(_("لا توجد أرصدة لتصفيرها في التاريخ المحدد للفرع %s") % self.branch_id.name)

        move_vals = {
            'date': self.date,
            'journal_id': self.journal_id.id,
            'ref': self.ref,
            'line_ids': move_data['move_lines'],
        }
        if hasattr(self.env['account.move'], 'branch_id'):
            move_vals['branch_id'] = self.branch_id.id

        move = self.env['account.move'].create(move_vals)
        move.action_post()

        if move_data['has_warning']:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('تحذير'),
                    'message': move_data['warning_message'],
                    'type': 'warning',
                    'sticky': True,
                    'next': {
                        'type': 'ir.actions.act_window',
                        'res_model': 'account.move',
                        'view_mode': 'form',
                        'res_id': move.id,
                    }
                }
            }
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': move.id,
        }
