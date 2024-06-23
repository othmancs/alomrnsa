# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

import logging
import pprint

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class TelrController(http.Controller):

    _return_url = '/payment/telr/return'

    @http.route(_return_url, type='http', auth='public', methods=['GET'], csrf=False, save_session=False)
    def telr_return_from_redirect(self, **post):
        txid = post.get('id')
        tx = request.env['payment.transaction'].sudo().browse(int(txid))
        post.update(tx._get_telr_tx_status())
        _logger.info('Telr: entering form_feedback with post data %s', pprint.pformat(post))
        request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
            'telr', post
        )
        tx._handle_notification_data('telr', post)
        return request.redirect('/payment/status')
