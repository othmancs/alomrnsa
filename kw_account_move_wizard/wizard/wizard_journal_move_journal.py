import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class KwJMoveJ(models.TransientModel):
    _name = 'kw.journal.move.journal.wizard'
    _description = 'Journal Cash Move to Journal Wizard'

    from_journal_id = fields.Many2one(
        comodel_name='account.journal', required=True, )
    to_journal_id = fields.Many2one(
        comodel_name='account.journal', required=True, )
    from_account_id = fields.Many2one(
        comodel_name='account.account', required=True, )
    to_account_id = fields.Many2one(
        comodel_name='account.account', required=True, )
    middleware_account_id = fields.Many2one(
        comodel_name='account.account',
        default=lambda self: self.env['account.account'].search(
            [('code', '=', '333000')], limit=1),
        required=True, )
    price = fields.Float(
        digits='Account', required=True)
    ref = fields.Char(
        string='Reference', )
    account_date = fields.Date(
        string='Date', required=True, index=True,
        default=fields.Date.context_today, )

    @api.onchange('from_journal_id')
    def check_is_from_availeble_account(self):
        if self.from_journal_id and self.from_journal_id.default_account_id:
            self.sudo().from_account_id = \
                self.from_journal_id.default_account_id.id
        else:
            self.sudo().from_account_id = False

    @api.onchange('to_journal_id')
    def check_is_to_availeble_account(self):
        if self.to_journal_id and self.to_journal_id.default_account_id:
            self.sudo().to_account_id = \
                self.to_journal_id.default_account_id.id
        else:
            self.sudo().to_account_id = False

    def create_from_account_move(self, account_id, journal_id):
        self.ensure_one()
        move = self.env['account.move'].create({
            'move_type': 'entry',
            'journal_id': journal_id.id,
            'date': self.account_date,
            'ref': self.ref,
            'line_ids': [
                (0, 0, {
                    'account_id': self.middleware_account_id.id,
                    'currency_id': self.env.company.currency_id.id,
                    'debit': self.price,
                    'credit': 0.0,
                }),
                (0, 0, {
                    'account_id': account_id.id,
                    'currency_id': self.env.company.currency_id.id,
                    'debit': 0.0,
                    'credit': self.price,
                }),
            ],
        })
        move.action_post()
        return True

    def create_to_account_move(self, account_id, journal_id):
        self.ensure_one()
        move = self.env['account.move'].create({
            'move_type': 'entry',
            'journal_id': journal_id.id,
            'date': self.account_date,
            'ref': self.ref,
            'line_ids': [
                (0, 0, {
                    'account_id': account_id.id,
                    'currency_id': self.env.company.currency_id.id,
                    'debit': self.price,
                    'credit': 0.0,
                }),
                (0, 0, {
                    'account_id': self.middleware_account_id.id,
                    'currency_id': self.env.company.currency_id.id,
                    'debit': 0.0,
                    'credit': self.price,
                }),
            ],
        })
        move.action_post()
        return True

    def apply_cash_move(self):
        self.ensure_one()
        if self.sudo().create_from_account_move(
                self.from_account_id, self.from_journal_id) and \
                self.sudo().create_to_account_move(
                    self.to_account_id, self.to_journal_id):
            return True
        return False
