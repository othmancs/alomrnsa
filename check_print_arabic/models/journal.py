from odoo import fields, models, _

class AccountJournal(models.Model):
    _inherit = 'account.journal'


    date_v = fields.Integer(string='Date Y-Pixcel')
    date_h = fields.Integer(string='Date X-Pixcel')

    place_v = fields.Integer(string='Place Y-Pixcel')
    place_h = fields.Integer(string='Place X-Pixcel')

    place = fields.Char(string='Place issue')

    partner_v = fields.Integer(string='Partner Y-Pixcel')
    partner_h = fields.Integer(string='Partner X-Pixcel')

    amount_v = fields.Integer(string='Amount Y-Pixcel')
    amount_h = fields.Integer(string='Amount X-Pixcel')

    amount_words_v = fields.Integer(string='Amount Words Y-Pixcel')
    amount_words_h = fields.Integer(string='Amount Words X-Pixcel')

    notes_v = fields.Integer(string='Notes Y-Pixcel')
    notes_h = fields.Integer(string='Notes X-Pixcel')

    font_size = fields.Integer(string='Font Size Pixcel')
