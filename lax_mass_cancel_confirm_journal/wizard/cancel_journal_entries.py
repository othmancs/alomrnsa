from odoo import api, models, _
from odoo.exceptions import UserError


class CancelJournalEntries(models.TransientModel):
    _name = 'cancel.journal.entries'
    _description = 'Cancel Journal Entries'

    def cancel_journal_entries(self):
        account_move_recs = self.env['account.move'].browse(
            self._context.get('active_ids'))
        account_move_recs.button_cancel()
        return True
