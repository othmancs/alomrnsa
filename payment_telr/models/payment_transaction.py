# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

import logging
import requests
from werkzeug import urls
from decimal import *

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
        payload = {
            "ivp_method": "create",
            "ivp_store": int(self.provider_id.telr_merchant_id),
            "ivp_authkey": self.provider_id.telr_api_key,
            "ivp_amount": round(float(self.amount), 2),
            "ivp_currency": self.currency_id.name,
            "ivp_test": 0 if self.provider_id.state == 'enabled' else 1,
            "ivp_cart": self.reference,
            "ivp_desc": self.reference,
            "return_auth": '%s?id=%s' % (urls.url_join(base_url, TelrController._return_url), str(self.id)),
            "return_decl": '%s?id=%s' % (urls.url_join(base_url, TelrController._return_url), str(self.id)),
            "return_can": '%s?id=%s' % (urls.url_join(base_url, TelrController._return_url), str(self.id))
        }
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        res = requests.request("POST", url, data=payload, headers=headers)
        response = res.json()

        if response.get('error'):
            raise ValidationError("Payment has been failed, no amount deducted! Message: %s" % response.get('error').get('note') or response.get('error').get('message'))

        self.telr_order_id = response.get('order').get('ref')
        processing_values['api_url'] = response.get('order').get('url')
        return processing_values

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
