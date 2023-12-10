from odoo import models, api, _, sql_db
from odoo.exceptions import UserError, ValidationError
import requests
import json
import re
import time
import logging

_logger = logging.getLogger(__name__)

class CheckPartnerMobile(models.TransientModel):
    _name = "check.partner.mobile"
    _description = "Check Partner Mobile"

    def check_whatsapps(self):
        context = dict(self._context or {})
        partners = self.env['res.partner'].browse(context.get('active_ids'))
        partner_to_check = self.env['res.partner']
        for partner in partners:
            if not partner.chat_id:
                partner_to_check += partner
        if not partner_to_check:
            raise UserError(_('There is no partner unchecked whatsapps mobile.'))
        partner_to_check.check_number_whatsapp()
        return {'type': 'ir.actions.act_window_close'}
