# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import logging
import requests
from werkzeug import urls
from decimal import *
from odoo.http import request
import socket
import ssl

from odoo import _, fields, models
from odoo.exceptions import ValidationError
from odoo.addons.payment_telr.controllers.main import TelrController


_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    telr_order_id = fields.Char(string='Telr Order ID')

    
    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return Telr-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of provider-specific processing values
        :rtype: dict
        """

        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'telr':
            return res

        base_url = self.provider_id.get_base_url()
        url = "https://secure.telr.com/gateway/order.json"

        bill_fname = self.env['res.partner'].search([('id', '=', int(self.partner_id))]).name
        bill_addr1 = self.env['res.partner'].search([('id', '=', int(self.partner_id))]).street
        bill_addr2 = self.env['res.partner'].search([('id', '=', int(self.partner_id))]).street2
        bill_city = self.env['res.partner'].search([('id', '=', int(self.partner_id))]).city
        bill_region_id = self.env['res.partner'].search([('id', '=', int(self.partner_id))]).state_id
        bill_zip = self.env['res.partner'].search([('id', '=', int(self.partner_id))]).zip
        bill_country_id = self.env['res.partner'].search([('id', '=', int(self.partner_id))]).country_id
        bill_email = self.env['res.partner'].search([('id', '=', int(self.partner_id))]).email
        bill_phone1 = self.env['res.partner'].search([('id', '=', int(self.partner_id))]).phone

        bill_region = self.env['res.country.state'].search([('id', '=', int(bill_region_id))]).name
        bill_country = self.env['res.country'].search([('id', '=', int(bill_country_id))]).code

        custrefid = self.env['res.partner'].search([('id', '=', int(self.partner_id))]).id
        
        payload = {
            "ivp_method": "create",
            "ivp_store": int(self.provider_id.telr_merchant_id),
            "ivp_authkey": self.provider_id.telr_api_key,
            "ivp_amount": round(float(self.amount), 2),
            "ivp_currency": self.currency_id.name,
            "ivp_test": 0 if self.provider_id.state == 'enabled' else 1,
            'ivp_framed': self.provider_id.telr_payment_mode,
            'ivp_lang': self.provider_id.telr_lang,
            'ivp_trantype': self.provider_id.telr_trans_type,
            "bill_fname": bill_fname,
            "bill_sname": bill_fname,
            "bill_addr1": bill_addr1,
            "bill_addr2": bill_addr2,
            "bill_city": bill_city,
            "bill_region": bill_region,
            "bill_zip": bill_zip,
            "bill_country": bill_country,
            "bill_email": bill_email,
            "bill_tel": bill_phone1,
            "ivp_cart": self.reference,
            "ivp_desc": self.reference,
            "return_auth": '%s?id=%s' % (urls.url_join(base_url, TelrController._return_url), str(self.id)),
            "return_decl": '%s?id=%s' % (urls.url_join(base_url, TelrController._return_url), str(self.id)),
            "return_can": '%s?id=%s' % (urls.url_join(base_url, TelrController._return_url), str(self.id))
        }
        
        current_user = self.env.user
        if current_user:
            logintype = self.env['res.users'].search([('id', '=', int(self.env.user.id))], limit=1).login    
            
            if logintype != 0:
                payload['bill_custref'] = custrefid
        
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        res = requests.request("POST", url, data=payload, headers=headers)
        response = res.json()

        if response.get('error'):
            raise ValidationError("Payment has been failed, no amount deducted! Message: %s" % response.get('error').get('note') or response.get('error').get('message'))

        self.telr_order_id = response.get('order').get('ref')
        processing_values['api_url'] = response.get('order').get('url')
        processing_values['ivp_framed'] = self.provider_id.telr_payment_mode
        
        return processing_values


    def _get_telr_seamless_tx(self, data):
    
        sefldata = data['processing_values']
        tx_record  = self.env['payment.transaction'].search([('reference', '=', sefldata['reference'])])   
        provider_data = request.env['payment.provider'].sudo().browse(sefldata['provider_id'])
        bill_fname = self.env['res.partner'].search([('id', '=', int(sefldata['partner_id']))]).name
        
        base_url = self.provider_id.get_base_url()
        url = "https://secure.telr.com/gateway/order.json"

        bill_fname = self.env['res.partner'].search([('id', '=', int(sefldata['partner_id']))]).name
        bill_addr1 = self.env['res.partner'].search([('id', '=', int(sefldata['partner_id']))]).street
        bill_addr2 = self.env['res.partner'].search([('id', '=', int(sefldata['partner_id']))]).street2
        bill_city = self.env['res.partner'].search([('id', '=', int(sefldata['partner_id']))]).city
        bill_region_id = self.env['res.partner'].search([('id', '=', int(sefldata['partner_id']))]).state_id
        bill_zip = self.env['res.partner'].search([('id', '=', int(sefldata['partner_id']))]).zip
        bill_country_id = self.env['res.partner'].search([('id', '=', int(sefldata['partner_id']))]).country_id
        bill_email = self.env['res.partner'].search([('id', '=', int(sefldata['partner_id']))]).email
        bill_phone1 = self.env['res.partner'].search([('id', '=', int(sefldata['partner_id']))]).phone
        
        bill_region = self.env['res.country.state'].search([('id', '=', int(bill_region_id))]).name
        bill_country = self.env['res.country'].search([('id', '=', int(bill_country_id))]).code

        custrefid = self.env['res.partner'].search([('id', '=', int(sefldata['partner_id']))]).id
        
        currency = request.env['res.currency'].browse(sefldata['currency_id'])
        
        payload = {
            "ivp_method": "create",
            "ivp_store": int(provider_data.telr_merchant_id),
            "ivp_authkey": provider_data.telr_api_key,
            "ivp_amount": round(float(sefldata['amount']), 2),
            "ivp_currency": currency.name,
            "ivp_test": 0 if provider_data.state == 'enabled' else 1,
            'ivp_framed': 2 if int(provider_data.telr_payment_mode) == 10 else provider_data.telr_payment_mode,
            'ivp_lang': provider_data.telr_lang,
            'ivp_trantype': provider_data.telr_trans_type,
            "bill_fname": bill_fname,
            "bill_sname": bill_fname,
            "bill_addr1": bill_addr1,
            "bill_addr2": bill_addr2,
            "bill_city": bill_city,
            "bill_region": bill_region,
            "bill_zip": bill_zip,
            "bill_country": bill_country,
            "bill_email": bill_email,
            "bill_tel": bill_phone1,
            "ivp_cart": sefldata['reference'],
            "ivp_desc": sefldata['reference'],
            'ivp_paymethod':'card',
            'card_token':data['telr_payment_token'],
            "return_auth": '%s?id=%s' % (urls.url_join(base_url, TelrController._return_url), str(tx_record.id)),
            "return_decl": '%s?id=%s' % (urls.url_join(base_url, TelrController._return_url), str(tx_record.id)),
            "return_can": '%s?id=%s' % (urls.url_join(base_url, TelrController._return_url), str(tx_record.id))
        }
        
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        res = requests.request("POST", url, data=payload, headers=headers)
        response = res.json()
        
        if response.get('error'):
            raise ValidationError("Payment has been failed, no amount deducted! Message: %s" % response.get('error').get('note') or response.get('error').get('message'))

        tx_record.telr_order_id = response.get('order').get('ref')
        self.env.cr.commit()
        return response.get('order').get('url')  



    def _get_telr_tx_status(self):
        url = "https://secure.telr.com/gateway/order.json"
        payload = {
            "ivp_method": "check",
            "ivp_store": int(self.provider_id.telr_merchant_id),
            "ivp_authkey": self.provider_id.telr_api_key,
            "order_ref": self.telr_order_id,
        }
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        res = requests.request("POST", url, data=payload, headers=headers)
        response = res.json()
        return response
        
    def _get_telr_save_cards(self, data, partner_id):
        custrefid = ''
        savedcardslist = []
        current_user = self.env.user

        if current_user:
            logintype = self.env['res.users'].search([('id', '=', int(self.env.user.id))], limit=1).login
            if logintype != 0:
                custrefid = self.env['res.partner'].search([('id', '=', int(partner_id))]).id

        if custrefid != '':
            url = "https://secure.telr.com/gateway/savedcardslist.json"
            payload = {
                "api_storeid": data.telr_merchant_id,
                "api_authkey": data.telr_api_key,
                "api_testmode": 0 if data.state == 'enabled' else 1,
                "api_custref": custrefid,
            }
     
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            res = requests.request("POST", url, data=payload, headers=headers)
            response = res.json()

            if response['SavedCardListResponse']['Code'] == 200:
                for i, card_info in enumerate(response['SavedCardListResponse']['data']):
                    savedcardslist.append({'txn_id': card_info['Transaction_ID'], 'name': card_info['Name']})
                    
            return savedcardslist
        else:
            return savedcardslist    

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ Override of payment to find the transaction based on Telr data.

        :param str provider_code: The code of the provider that handled the transaction
        :param dict notification_data: The notification data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if inconsistent data were received
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'telr' or len(tx) == 1:
            return tx

        notification_data = notification_data.get('order')
        reference = notification_data.get('cartid')
        if not reference:
            raise ValidationError(
                "Telr: " + _(
                    "Received data with missing reference %(r)s.", r=reference
                )
            )

        tx = self.search([('reference', '=', reference), ('provider_code', '=', 'telr')])
        if not tx:
            raise ValidationError(
                "Telr: " + _("No transaction found matching reference %s.", reference)
            )

        return tx

    def _process_notification_data(self, notification_data):
        """ Override of `payment' to process the transaction based on Telr data.

        Note: self.ensure_one()

        :param dict notification_data: The notification data sent by the provider.
        :return: None
        :raise ValidationError: If inconsistent data are received.
        """
        super()._process_notification_data(notification_data)
        if self.provider_code != 'telr':
            return
        
       
        if self.operation == 'refund':
            status = notification_data['status']
            message = notification_data['message']
            tranref = notification_data['tranref']
            
            if status == 'A':
                self._set_done()
                self.env.ref('payment.cron_post_process_payment_tx')._trigger()
                self.write({'provider_reference': tranref})
            else:
                self._set_error(
                    "Telr: " + message
                )      
                
        elif 'state' in notification_data and notification_data['state'] == 'capture':
            
            status = notification_data['status']
            message = notification_data['message']
            tranref = notification_data['tranref']
           
            if status == 'A':
                self._set_done()
                self.write({'provider_reference': tranref})
            else:
                self._set_error(
                    "Telr: " + message
                )
            
        elif 'state' in notification_data and notification_data['state'] == 'void':
            
            status = notification_data['status']
            message = notification_data['message']
            tranref = notification_data['tranref']
            
            if status == 'A':
                self._set_canceled()
                self.write({'provider_reference': tranref})
            else:
                self._set_error(
                    "Telr: " + message
                )
              
        else:
        
            data = notification_data.get('order')
            if data.get('ref') != self.telr_order_id:
                raise ValidationError(
                    "Telr: " + _(
                        "The order reference returned by telr %(ref)s does not match the transaction "
                        "Telr Order ID %(tref)s.", ref=data.get('ref'), tref=self.telr_order_id
                    )
                )
            if round(float(data.get('amount')), 2) != round(float(self.amount), 2):
                _logger.error(
                    "the paid amount (%(amount)s) does not match for the transaction with reference %(reference)s", amount=data.get('amount'), reference=self.reference
                )
                raise ValidationError("Telr: " + _("The amount does not match the transaction amount."))
            if data.get('currency') != self.currency_id.name:
                raise ValidationError(
                    "Telr: " + _(
                        "The currency returned by telr %(rc)s does not match the transaction "
                        "currency %(tc)s.", rc=data.get('currency'), tc=self.currency_id.name
                    )
                )

            status = data.get('status')

            self.write({
                'provider_reference': data.get('transaction') and data.get('transaction').get('ref'),
            })

            if status.get('code') == 3:
                _logger.info('Telr payment for tx %s: set as DONE' % (self.reference))
                self._set_done()
            elif status.get('code') == 2:
                _logger.info('Telr payment for tx %s: set as AUTHORIZED' % (self.reference))
                self._set_authorized()
            elif status.get('code') == 1:
                _logger.info('Telr payment for tx %s: set as PENDING' % (self.reference))
                self._set_pending()
            elif status.get('code') == -2:
                _logger.info('Telr payment for tx %s: set as CANCELLED' % (self.reference))
                self._set_canceled()
            else:
                _logger.warning("received data with invalid status: %s", status.get('text'))
                self._set_error(
                    "Telr: " + _("Received data with invalid status: %s", status.get('text'))
                )

    def _send_refund_request(self, amount_to_refund=None):
        """ Request the provider handling the transaction to refund it.

        For a provider to support refunds, it must override this method and make an API request to
        make a refund.

        Note: `self.ensure_one()`

        :param float amount_to_refund: The amount to be refunded.
        :return: The refund transaction created to process the refund request.
        :rtype: recordset of `payment.transaction`
        """
        
        
        refund_tx = super()._send_refund_request(amount_to_refund=amount_to_refund)
        if self.provider_code != 'telr':
            return refund_tx
                    
        if self.provider_id.telr_remote_key == 0:            
            raise ValidationError(
                "Telr: " + _(
                    "Refund do not initiate because Remote API Authentication Key is blank in Telr payment configuration"
                )
            )
        
        self.ensure_one()
        self._ensure_provider_is_not_disabled()

        refund_response = self._telr_remote_xml_req(amount_to_refund, 'refund', 'Initiate refund request')
        
        responseXml = ET.fromstring(refund_response)
        status = responseXml.find('auth').find('status').text
        message = responseXml.find('auth').find('message').text
        tranref = responseXml.find('auth').find('tranref').text
        
        notification_data = {'status': status, 'message': message, 'tranref': tranref, 'state':'refund'}
        refund_tx._handle_notification_data('telr', notification_data)       
        refund_tx._log_sent_message()
        
        return refund_tx
        
        
    def _send_capture_request(self):
        """ Override of payment to simulate a capture request.

        Note: self.ensure_one()

        :return: None
        """
        super()._send_capture_request()
        if self.provider_code != 'telr':
            return
        
        if self.provider_id.telr_remote_key == 0:            
            raise ValidationError(
                "Telr: " + _(
                    "Capture request do not initiate because Remote API Authentication Key is blank in Telr payment configuration"
                )
            )
        
        capture_response = self._telr_remote_xml_req(round(float(self.amount), 2), 'capture', 'Initiate capture request')
        
        responseXml = ET.fromstring(capture_response)
        status = responseXml.find('auth').find('status').text
        message = responseXml.find('auth').find('message').text
        tranref = responseXml.find('auth').find('tranref').text
        
        notification_data = {'status': status, 'message': message, 'tranref': tranref, 'state':'capture'}
        self._handle_notification_data('telr', notification_data)

    def _send_void_request(self):
        """ Override of payment to simulate a void request.

        Note: self.ensure_one()

        :return: None
        """
        super()._send_capture_request()
        if self.provider_code != 'telr':
            return
        
        if self.provider_id.telr_remote_key == 0:
            raise ValidationError(
                "Telr: " + _(
                    "Void request do not initiate because Remote API Authentication Key is blank in Telr payment configuration"
                )
            )
        
        void_response = self._telr_remote_xml_req(round(float(self.amount), 2), 'void', 'Initiate void request')

        responseXml = ET.fromstring(void_response)
        status = responseXml.find('auth').find('status').text
        message = responseXml.find('auth').find('message').text
        tranref = responseXml.find('auth').find('tranref').text
        
        notification_data = {'status': status, 'message': message, 'tranref': tranref, 'state':'void'}
        self._handle_notification_data('telr', notification_data)

    def _telr_remote_xml_req(self, refund_amount, request_type, refund_description):
        url = "https://secure.telr.com/gateway/remote.xml"
        
        store_id = int(self.provider_id.telr_merchant_id)
        """auth_key = self.provider_id.telr_api_key"""
        """auth_key = 'BG88b#FBFpX^xSzw'"""
        auth_key = self.provider_id.telr_remote_key
        cart_id = self.reference
        test_method = 0 if self.provider_id.state == 'enabled' else 1
        refund_currency = self.currency_id.name
        
        if request_type == 'refund':
            refund_reference = self.provider_reference
        else:
            refund_reference = self.telr_order_id
           
        refund_reference = self.provider_reference
        
        xml_payload = """ 
        <?xml version='1.0' encoding='UTF-8'?>
        <remote>
            <store>{store_id}</store>
            <key>{auth_key}</key>
            <tran>
                <type>{request_type}</type>
                <class>ecom</class>
                <cartid>{cart_id}</cartid>
                <description>{refund_description}</description>
                <test>{test_method}</test>
                <currency>{refund_currency}</currency>
                <amount>{refund_amount}</amount>
                <ref>{refund_reference}</ref>
            </tran>
        </remote>        
        """
        
        formatted_payload = xml_payload.format(store_id=store_id, 
                            auth_key=auth_key, 
                            request_type=request_type, 
                            cart_id=cart_id, 
                            refund_description=refund_description, 
                            test_method=test_method,
                            refund_currency=refund_currency,
                            refund_amount=refund_amount,
                            refund_reference=refund_reference,
                            )
        
        headers = {'content-type':'application/xml'}
        response_xml_as_string = requests.request("POST", url, data=formatted_payload, headers=headers)   
               
        return response_xml_as_string.text       
    
    def check_ssl(self, hostname):
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                return ssock.version()
                
                