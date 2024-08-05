from odoo import api, models, _
from odoo.exceptions import UserError


class ConfirmJournalEntries(models.TransientModel):
    _name = 'confirm.journal.entries'
    _description = 'Confirm Journal Entries'

    def confirm_journal_entries(self):
        account_move_recs = self.env['account.move'].browse(
            self._context.get('active_ids'))
        account_move_recs.action_post()
        return True
