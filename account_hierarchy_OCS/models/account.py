from odoo import models, fields, api

class AccountAccount(models.Model):
    _inherit = 'account.account'

    level = fields.Integer(string='المستوى', compute='_compute_level', store=True)
    custom_parent_id = fields.Many2one('account.account', string='الحساب الأب المخصص')
    custom_child_ids = fields.One2many('account.account', 'custom_parent_id', string='الحسابات الفرعية المخصصة')

    @api.depends('code', 'custom_parent_id')
    def _compute_level(self):
        for account in self:
            level = 1
            parent = account.custom_parent_id
            while parent:
                level += 1
                parent = parent.custom_parent_id
            account.level = level

    def write(self, vals):
        res = super(AccountAccount, self).write(vals)
        if 'custom_parent_id' in vals:
            self._compute_level()
            # إعادة حساب المستويات للحسابات الفرعية
            for account in self:
                account.custom_child_ids._compute_level()
        return res