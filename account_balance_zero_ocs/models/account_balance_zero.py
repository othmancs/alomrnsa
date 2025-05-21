from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

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

    def action_zero_balances(self):
        self.ensure_one()
        
        # الحصول على جميع الحسابات التي لها رصيد
        Account = self.env['account.account']
        Move = self.env['account.move']
        MoveLine = self.env['account.move.line']
        
        accounts = Account.search([('deprecated', '=', False)])
        
        if not accounts:
            raise UserError(_("لا توجد حسابات متاحة لتصفير الأرصدة"))
        
        # إنشاء قيد اليومية
        move_vals = {
            'date': self.date,
            'journal_id': self.journal_id.id,
            'ref': self.ref,
            'line_ids': [],
        }
        
        # إعداد بنود القيد
        for account in accounts:
            balance = account._compute_balance({'date_to': self.date})
            
            if balance:
                # حساب الرصيد
                amount = abs(balance)
                debit = balance > 0 and amount or 0.0
                credit = balance < 0 and amount or 0.0
                
                # إضافة بند القيد
                move_vals['line_ids'].append((0, 0, {
                    'account_id': account.id,
                    'debit': debit,
                    'credit': credit,
                    'name': _('تصفير رصيد الإغلاق'),
                }))
        
        # إنشاء القيد فقط إذا كان هناك أرصدة لتصفيرها
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