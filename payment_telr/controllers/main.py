# -*- coding: utf-8 -*-

import logging
import pprint

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class TelrController(http.Controller):

    _return_url = '/payment/telr/return'    
    _ivp_callback_url = '/payment/telr/ivpcallback'
    
    
    @http.route(_return_url, type='http', auth='public', methods=['GET'], csrf=False, save_session=False)
    def telr_return_from_redirect(self, **post):
        txid = post.get('id')
        print(post)
        tx = request.env['payment.transaction'].sudo().browse(int(txid))
        post.update(tx._get_telr_tx_status())
        _logger.info('Telr: entering form_feedback with post data %s', pprint.pformat(post))
        request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
            'telr', post
        )
        tx._handle_notification_data('telr', post)
        return request.redirect('/payment/status')
    
    @http.route(_ivp_callback_url, type='http', auth='public', methods=['POST', 'GET'], csrf=False, save_session=False)
    def telr_ivpcallback_return(self, **kwargs):
        txid = request.httprequest.args.get('id')
        tx = request.env['payment.transaction'].sudo().browse(int(txid))
        print(post) 
        
    @http.route('/payment/telr/getinfo', type='json', auth='public')
    def get_provider_info(self, **data):
        
        frameHeight = 320
        
        provider_sudo = request.env['payment.provider'].sudo().browse(data['provider_id'])
        currency = request.env['res.currency'].browse(data['currency_id'])
        
        savedCards = request.env['payment.transaction'].sudo()._get_telr_save_cards(provider_sudo, data['partner_id'])
        if len(savedCards) > 0:
            for value in savedCards:
                frameHeight += 30;
                frameHeight += (len(savedCards) * 110)
                
        return {
            'store_id': provider_sudo.telr_merchant_id,
            'currency_name': currency.name,
            'test_mode': 0 if provider_sudo.state == 'enabled' else 1,
            'telr_payment_mode': provider_sudo.telr_payment_mode,
            'saved_cards':savedCards,
            'frame_height':frameHeight,
            'language':provider_sudo.telr_lang
        }
        
    @http.route('/payment/telr/process_payment', type='json', auth='public', csrf=False, save_session=False)
    def telr_process_payment(self, **data):
       
        return request.env['payment.transaction'].sudo()._get_telr_seamless_tx(data)
         