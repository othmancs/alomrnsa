# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, sql_db, _
from odoo.tools.float_utils import float_is_zero
from odoo.tools.mimetypes import guess_mimetype
import requests
import json
import base64
from datetime import datetime
import time
import html2text
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def _get_average_sold(self):
        for quant in self:
            # self._cr.execute(''' 
            #     SELECT ct.name, sum(sr.product_uom_qty) from sale_report sr
            #     LEFT JOIN crm_team ct ON ct.id = sr.team_id
            #     WHERE sr.product_id = %s
            #     AND sr.date >= date_trunc('month', CURRENT_DATE)
            #     GROUP BY ct.name
            # ''' % quant.product_id.id)
            self._cr.execute(''' 
                SELECT ct.name, sum(sol.product_uom_qty) from sale_order_line sol
                LEFT JOIN sale_order so ON so.id=sol.order_id
                LEFT JOIN crm_team ct ON ct.id = so.team_id
                WHERE sol.product_id = %s
                AND so.date_order >= date_trunc('month', CURRENT_DATE)
                GROUP BY ct.name
            ''' % quant.product_id.id)
            print ('===self._cr.fetchall()===',self._cr.fetchall())
            sale_reports = dict(self._cr.fetchall())
            quant.average_sold = sale_reports
            # self._cr.execute(''' 
            #     SELECT sl.name, sum(sq.available_quantity) from stock_quant sq
            #     LEFT JOIN stock_location sl ON sl.id = sq.location_id
            #     WHERE sq.product_id = %s
            #     --AND sq.date >= date_trunc('month', CURRENT_DATE)
            #     GROUP BY sl.name
            # ''' % quant.product_id.id)
            # stock_reports = dict(self._cr.fetchall())
            stock_reports = self.env['stock.quant'].read_group(
                [('product_id','=',quant.product_id.id), ('location_id.usage','=','internal')], 
                ['location_id', 'available_quantity'], ['location_id'])
            mapped_data = dict([(self.env['stock.location'].browse(stock['location_id'][0]).display_name, stock['available_quantity']) for stock in stock_reports])
            quant.available_qty = mapped_data
            # for partner in self:
            #     partner.bank_account_count = mapped_data.get(partner.id, 0)

    minimum_quantity = fields.Float(
        'Min. Quantity',
        help='Minimum quantity of products in this quant, in the default unit of measure of the product')
    average_sold = fields.Text('Avg sold per month', compute='_get_average_sold')
    available_qty = fields.Text('Location Qty', compute='_get_average_sold')

    @api.model
    def _get_inventory_fields_write(self):
        """ Returns a list of fields user can edit when he want to edit a quant in `inventory_mode`.
        """
        return ['inventory_quantity', 'minimum_quantity']

    def _get_whatsapp_server(self):
        WhatsappServer = self.env['ir.whatsapp_server']
        whatsapp_ids = WhatsappServer.search([('status','=','authenticated')], order='sequence asc', limit=1)
        if whatsapp_ids:
            return whatsapp_ids
        return False

    def _send_whatsapp_automatic(self):
        for quant in self:
            new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
            MailMessage = self.env['mail.message']
            WhatsappComposeMessage = self.env['whatsapp.compose.message']
            template_id = self.env.ref('aos_whatsapp_stock.stock_quant_minimum_stock_status', raise_if_not_found=False)
            if self._get_whatsapp_server() and self._get_whatsapp_server().status == 'authenticated':
                KlikApi = self._get_whatsapp_server().klikapi()       
                KlikApi.auth()         
                template = template_id.generate_email(quant.id, ['body_html'])
                body = template.get('body_html')
                subject = template.get('subject')
                # try:
                #     body = body.replace('_PARTNER_', quant.partner_id.name)
                # except:
                #     _logger.warning('Failed to send Message to WhatsApp number %s', quant.partner_id.whatsapp)         
                attachment_ids = []
                chatIDs = []
                message_data = {}
                send_message = {}
                status = 'error'
                partners = self.env['res.partner']
                if quant.location_id.whatsapp_partner_ids:
                    partners = quant.location_id.whatsapp_partner_ids
                    # if pick.partner_id.child_ids:
                    #     #ADDED CHILD FROM PARTNER
                    #     for partner in pick.partner_id.child_ids:
                    #         partners += partner
                print ('==partners==',partners)  
                for partner in partners:
                    if partner.whatsapp:
                        #SEND MESSAGE
                        whatsapp = partner._formatting_mobile_number()
                        message_data = {
                            'method': 'sendMessage',
                            'phone': whatsapp,
                            'body': html2text.html2text(body),
                            'origin': quant.product_id.display_name,
                            'link': '',
                        }
                        print ('--message_data-',message_data)
                        if partner.chat_id:
                            message_data.update({'chatId': partner.chat_id, 'phone': '', 'origin': quant.product_id.display_name, 'link': False})
                        data_message = json.dumps(message_data)
                        send_message = KlikApi.post_request(method='sendMessage', data=data_message)
                        if send_message.get('message')['sent']:
                            chatID = send_message.get('chatID')
                            status = 'send'
                            partner.chat_id = chatID
                            chatIDs.append(chatID)
                            _logger.warning('Success to send Message to WhatsApp number %s', whatsapp)
                        else:
                            status = 'error'
                            _logger.warning('Failed to send Message to WhatsApp number %s', whatsapp)
                        new_cr.commit()
                        #time.sleep(3)                
                AllchatIDs = ';'.join(chatIDs)
                vals = WhatsappComposeMessage._prepare_mail_message(self.env.user.partner_id.id, AllchatIDs, quant and quant.id,  'stock.quant', body, message_data, subject, partners.ids, attachment_ids, send_message, status)
                MailMessage.sudo().create(vals)
                new_cr.commit()
                #time.sleep(3)

    def write(self, vals):
        """ Override to handle the "inventory mode" and create the inventory move. """
        # allowed_fields = self._get_inventory_fields_write()
        # if self._is_inventory_mode() and any(field for field in allowed_fields if field in vals.keys()):
        #     if any(quant.location_id.usage == 'inventory' for quant in self):
        #         # Do nothing when user tries to modify manually a inventory loss
        #         return
        #     if any(field for field in vals.keys() if field not in allowed_fields):
        #         raise UserError(_("Quant's editing is restricted, you can't do this operation."))
        #     self = self.sudo()
        #     return super(StockQuant, self).write(vals)
        # available_quantity < minimum_quantity
        result = super(StockQuant, self).write(vals)
        quant = self.sudo()
        #rint ('=GET MIN=',quant.minimum_quantity,quant.available_quantity,quant.available_quantity <= quant.minimum_quantity)
        if quant.minimum_quantity and quant.available_quantity <= quant.minimum_quantity:
            print ('==LOW QUANTITY==')
            self._send_whatsapp_automatic()
        return result