from odoo import fields , models,api,tools,_
from datetime import datetime,timedelta
from odoo.exceptions import ValidationError
# from odoo import amount_to_text

class SettingMain(models.TransientModel):

    _inherit = 'res.config.settings'

    petty_account_id = fields.Many2one('account.account', 'Petty cash Account',
                                       config_parameter='custody_request.petty_account_id')
