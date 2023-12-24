# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from odoo import fields, models


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('telr', 'Telr')], ondelete={'telr': 'set default'})
    telr_merchant_id = fields.Char(string='Store ID', required_if_provider='telr', groups='base.group_user')
    telr_api_key = fields.Char('API Key', required_if_provider='telr', groups='base.group_user')
