# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#################################################################################

from odoo import models, fields, api
import logging

class PaymentProof(models.Model):
    _inherit = 'sale.order'
    _description = 'Payment Proof Attachments'

    payment_proof = fields.Binary(attachment=True)
    payment_proof_name = fields.Char(default="proof.jpg")