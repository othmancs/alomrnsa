# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    credit_account_id = fields.Many2one('account.account', config_parameter='hr_loan.credit_account_id')
    debit_account_id = fields.Many2one('account.account', config_parameter='hr_loan.debit_account_id')
    journal_id = fields.Many2one('account.journal', config_parameter='hr_loan.journal_id')

