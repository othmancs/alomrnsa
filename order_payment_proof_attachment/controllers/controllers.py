# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#################################################################################
from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
import base64

import logging
_logger = logging.getLogger(__name__)

class ProofUploadController(WebsiteSale):
    @http.route(["/upload/payment/proof"],type='http', auth='public', website=True, sitemap=False)
    def upload_payment_proof(self,**post):
        to_confirm = post.get("to_confirm",False)
        sale_order_id = post.get('sale_order_id',False)
        order = request.env['sale.order'].sudo().browse(int(sale_order_id))
        attachment = post.get('txn_proof',False)
        email_template_id = request.env.ref('order_payment_proof_attachment.payment_receipt_email_template')
        if order and attachment:
            try:
                order.payment_proof = base64.encodebytes(attachment.read())
                order.payment_proof_name = attachment.filename
                if email_template_id:
                    email_attachment = {
                        'name': attachment.filename,
                        'datas': order.payment_proof,
                        'res_model': 'sale.order',
                        'type': 'binary'
                        }

                    email_attachment_id = request.env['ir.attachment'].sudo().create(email_attachment)
                    email_template_id.sudo().attachment_ids = email_attachment_id
                    order.message_post_with_template(email_template_id.id)
            except Exception as e:
                if to_confirm:
                    return request.redirect("/my/orders/"+sale_order_id)
                else:
                    _logger.info("==================%r",e)
                    return request.redirect("/shop/confirmation")
                    
        if to_confirm:
            return request.redirect("/my/orders/"+sale_order_id)
        else:
            return request.redirect("/shop/confirmation")
