# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import requests
from email import encoders
from email.charset import Charset
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formataddr, formatdate, getaddresses, make_msgid
import logging
import re
import smtplib
import json
import threading
from datetime import timedelta
from ..klikapi import KlikApi

import html2text

from odoo import api, fields, models, tools, _, sql_db
from odoo.exceptions import except_orm, UserError
from odoo.tools import ustr, pycompat

_logger = logging.getLogger(__name__)

SMTP_TIMEOUT = 60

class WaKlikodoo(models.TransientModel):
    _name = "wa.klikodoo.popup"
    _description = "Wa Klikodoo"
    
    qr_scan = fields.Binary("QR Scan")
    
class IrWhatsappServer(models.Model):
    """Represents an SMTP server, able to send outgoing emails, with SSL and TLS capabilities."""
    _name = "ir.whatsapp_server"
    _description = 'Whatsapp Server'

    name = fields.Char(string='Description', required=True, index=True)
    sequence = fields.Integer(string='Priority', default=10, help="When no specific mail server is requested for a mail, the highest priority one "
                                                                  "is used. Default priority is 10 (smaller number = higher priority)")
    active = fields.Boolean(default=True)
    klik_key = fields.Char("KlikApi Key", help="Optional key for SMTP authentication")
    klik_secret = fields.Char("KlikApi Secret", help="Optional secret for SMTP authentication")
    qr_scan = fields.Binary("QR Scan")
    whatsapp_number = fields.Char('Whatsapp Number')
    whatsapp_webhook = fields.Char('Whatsapp Webhook')
    status = fields.Selection([('init','Initial Status'),
                               ('loading', 'Loading'),
                               ('got qr code', 'QR Code'),
                               ('authenticated', 'Authenticated')], default='init', string="Status")
    hint = fields.Char(string='Hint', readonly=True, default="Configure Token and Instance")
    message_ids = fields.One2many('mail.message', 'whatsapp_server_id', string="Mail Message")    
    message_counts = fields.Integer('Message Sent Counts', compute='_get_mail_message_whatsapp')
    message_response = fields.Text('Message Response', compute='_get_mail_message_whatsapp')
    allowed_user_ids = fields.Many2many('res.users', 'allowed_user_ids_rel', string="Allowed Users",
        domain=[('share', '=', False)])
    notify_user_ids = fields.Many2many('res.users', 'notify_user_ids_rel', string="Channel Notification", default=lambda self: self.env.user,
        domain=[('share', '=', False)], required=True, tracking=5,
        help="Users to notify when a message is received and there is no template send in last 15 days")
    notes = fields.Text(readonly=True)

    @api.model
    def _find_default_for_server(self):
        return [
            # ('model', '=', model_name),
            # ('wa_template', '=', True),
            ('status','=','authenticated'),
            '|',
                ('allowed_user_ids', '=', False),
                ('allowed_user_ids', 'in', self.env.user.ids)
        ]

    def klikapi(self):
        self.ensure_one()
        APIUrl = self.env['ir.config_parameter'].sudo().get_param('aos_whatsapp.url_klikodoo_whatsapp_server')
        return KlikApi(APIUrl, self.klik_key, self.klik_secret)
    
    def _get_mail_message_whatsapp(self):
        for was in self:
            try:
                KlikApi = was.klikapi()
                KlikApi.auth()
                was.message_counts = KlikApi.get_count()
                was.message_response = KlikApi.get_limit()
            except:
                was.message_counts = 0
                was.message_response = ''

    
    def _formatting_mobile_number(self, number):
        for rec in self:
            module_rec = self.env['ir.module.module'].sudo().search_count([
                ('name', '=', 'crm_phone_validation'),
                ('state', '=', 'installed')])
            country_code = str(rec.partner_id.country_id.phone_code)# if rec.partner_id.country_id else str(self.company_id.country_id.phone_code)
            country_count = len(str(rec.partner_id.country_id.phone_code))
            whatsapp_number = rec.partner_id.whatsapp
            if rec.partner_id.whatsapp[:country_count] == str(rec.partner_id.country_id.phone_code):
                #JIKA DEPAANYA 62
                whatsapp_number = rec.partner_id.whatsapp
            elif rec.partner_id.whatsapp[0] == '0':
                #JIKA DEPANNYA 0
                if rec.partner_id.whatsapp[1:country_count+1] == str(rec.partner_id.country_id.phone_code):
                    #COUNTRY CODE UDH DIDEPAN
                    whatsapp_number = rec.partner_id.whatsapp[1:]
                else:
                    whatsapp_number = country_code + rec.partner_id.whatsapp[1:]
            return whatsapp_number
            # return module_rec and re.sub("[^0-9]", '', number) or \
            #     str(rec.partner_id.country_id.phone_code
            #         ) + number
    
    def klikapi_status(self):
        #WhatsApp is open on another computer or browser. Click “Use Here” to use WhatsApp in this window.
        data = {}
        KlikApi = self.klikapi()
        KlikApi.auth()
        #INJECT START == WHATSAPP NUMBER ON SERVER
        number_data = {
            'whatsapp_number': self.whatsapp_number,
            'whatsapp_webhook': self.whatsapp_webhook,
        }
        data_number = json.dumps(number_data)
        KlikApi.post_request(method='number', data=data_number)
        #=======================================================================
        data = KlikApi.get_request(method='status', data=data)
        # print ('---data---',data)
        if data.get('accountStatus') == 'loading':
            self.hint = 'Auth status is Loading! Please click QR Code/Use here again'
            self.status = 'loading'
            self.notes = ''
        elif data.get('accountStatus') == 'authenticated':
            #ALREADY SCANNED
            self.hint = 'Auth status Authenticated'
            self.status = 'authenticated'
            self.notes = ''
        elif data.get('qrCode'):
            #FIRST SCANNED OR RELOAD QR
            #print('33333')
            qrCode = data.get('qrCode').split(',')[1]
            self.qr_scan = qrCode
            self.status = 'got qr code'
            self.hint = 'To send messages, you have to authorise like for WhatsApp Web'
            self.notes = """1. Open the WhatsApp app on your phone
2. Press Settings->WhatsApp WEB and then plus
3. Scan a code and wait a minute
4. Keep your phone turned on and connected to the Internet
A QR code is valid only for 45 seconds. Message sennding will be available right after authorization."""
        else:
            #print('44444')
            #ERROR GET QR
            self.qr_scan = False
            self.status = 'init'
            self.hint = data.get('error')
            self.notes = ''
    
    def klikapi_logout(self):
        KlikApi = self.klikapi()
        KlikApi.auth()
        KlikApi.logout()
        self.write({'qr_scan': False, 'hint': 'Logout Success', 'notes': '', 'status': 'init'})
        
    
    def redirect_whatsapp_key(self):
        return {
            'type': 'ir.actions.act_url',
            'url': 'https://klikodoo.id/shop/product/whatsapp-api-14',
            'target': '_new',
        }
        
    @api.model
    def _send_whatsapp(self, numbers, message):
        """ Send whatsapp """
        KlikApi = self.klikapi()
        KlikApi.auth()
        new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
        for number in numbers:
            whatsapp = self._formatting_mobile_number(number)
            message_data = {
                'phone': whatsapp,
                'body': html2text.html2text(message),
            }
            data_message = json.dumps(message_data)
            send_message = KlikApi.post_request(method='sendMessage', data=data_message)
            if send_message.get('message')['sent']:
                _logger.warning('Success to send Message to WhatsApp number %s', whatsapp)
            else:
                _logger.warning('Failed to send Message to WhatsApp number %s', whatsapp)
            new_cr.commit()
        return True

    
    def _find_active_channel(self, sender_mobile_formatted, sender_name=False, create_if_not_found=False):
        """This method will find the active channel for the given sender mobile number."""
        allowed_old_msg_date = fields.Datetime.now() - timedelta(days=self.env['mail.message']._ACTIVE_THRESHOLD_DAYS)
        whatsapp_message = self.env['mail.message'].sudo().search(
            [
                # ('mobile_number_formatted', '=', sender_mobile_formatted),
                ('message_type','=','whatsapp'),
                ('create_date', '>', allowed_old_msg_date),
                # ('wa_template_id', '!=', False),
                # ('whatsapp_message_type','=',''),
                # ('state', 'not in', ['outgoing', 'error', 'cancel']),
            ], limit=1, order='id desc')
        return self.env['mail.channel'].sudo()._get_whatsapp_channel(
            whatsapp_number=sender_mobile_formatted,
            wa_account_id=self,
            sender_name=sender_name,
            create_if_not_found=create_if_not_found,
            related_message=whatsapp_message.whatsapp_message_id,
        )
 
    def _process_messages(self, value, attachments):
        """
            This method is used for processing messages with the values received via webhook.
            If any whatsapp message template has been sent from this account then it will find the active channel or
            create new channel with last template message sent to that number and post message in that channel.
            And if channel is not found then it will create new channel with notify user set in account and post message.
            Supported Messages
             => Text Message
             => Attachment Message with caption
             => Location Message
             => Contact Message
             => Message Reactions
        """
        # if 'messages' not in value and value.get('whatsapp_business_api_data', {}).get('messages'):
        #     value = value['whatsapp_business_api_data']

        # wa_api = WhatsAppApi(self)

        messages = value.get('messages', [])
        parent_id = False
        channel = False
        # print ('===messages===',value)
        sender_name = value['sendername']#value.get('contacts', [{}])[0].get('profile', {}).get('name')
        sender_mobile = value['sender']
        message_type = value['message_type']
        if 'context' in messages:
            # parent_whatsapp_message = self.env['whatsapp.message'].sudo().search([('msg_uid', '=', messages['context'].get('id'))])
            # if parent_whatsapp_message:
            #     parent_id = parent_whatsapp_message.mail_message_id
            if parent_id:
                channel = self.env['mail.channel'].sudo().search([('message_ids', 'in', parent_id.id)], limit=1)
        if not channel:
            # channel_domain = []
            # channel = self.env['mail.channel'].sudo().search(channel_domain, order='create_date desc', limit=1)
            channel = self._find_active_channel(sender_mobile, sender_name=sender_name, create_if_not_found=True)
        #print ('==channel==',channel,messages)
        kwargs = {
            'email_from': sender_name,
            'whatsapp_numbers': sender_mobile,
            'author_id': self.env['res.partner'].search([('whatsapp','=',sender_mobile)], limit=1).id,#channel.whatsapp_partner_id.id,
            'subtype_xmlid': 'mail.mt_comment',
            'body': messages,
            'whatsapp_status': 'send',#BIAR GA MASUK SCHEDULER
            # 'parent_id': parent_id.id if parent_id else None
        }
        # print ('==message_type=',message_type,attachments)
        if attachments:
            kwargs['attachments'] = attachments
        # if message_type == 'text':
        #     kwargs['body'] = plaintext2html(messages['text']['body'])
        # elif message_type == 'button':
        #     kwargs['body'] = messages['button']['text']
        # elif message_type in ('document', 'image', 'audio', 'video', 'sticker'):
        #     filename = messages[message_type].get('filename')
        #     mime_type = messages[message_type].get('mime_type')
        #     caption = messages[message_type].get('caption')
        #     datas = wa_api._get_whatsapp_document(messages[message_type]['id'])
        #     if not filename:
        #         extension = mimetypes.guess_extension(mime_type) or ''
        #         filename = message_type + extension
        #     kwargs['attachments'] = [(filename, datas)]
        #     if caption:
        #         kwargs['body'] = plaintext2html(caption)
        # elif message_type == 'location':
        #     url = Markup("https://maps.google.com/maps?q={latitude},{longitude}").format(
        #         latitude=messages['location']['latitude'], longitude=messages['location']['longitude'])
        #     body = Markup('<a target="_blank" href="{url}"> <i class="fa fa-map-marker"/> {location_string} </a>').format(
        #         url=url, location_string=_("Location"))
        #     if messages['location'].get('name'):
        #         body += Markup("<br/>{location_name}").format(location_name=messages['location']['name'])
        #     if messages['location'].get('address'):
        #         body += Markup("<br/>{location_address}").format(location_name=messages['location']['address'])
        #     kwargs['body'] = body
        # elif message_type == 'contacts':
        #     body = ""
        #     for contact in messages['contacts']:
        #         body += Markup("<i class='fa fa-address-book'/> {contact_name} <br/>").format(
        #             contact_name=contact.get('name', {}).get('formatted_name', ''))
        #         for phone in contact.get('phones'):
        #             body += Markup("{phone_type}: {phone_number}<br/>").format(
        #                 phone_type=phone.get('type'), phone_number=phone.get('phone'))
        #     kwargs['body'] = body
        # elif message_type == 'reaction':
        #     msg_uid = messages['reaction'].get('message_id')
        #     whatsapp_message = self.env['whatsapp.message'].sudo().search([('msg_uid', '=', msg_uid)])
        #     if whatsapp_message:
        #         partner_id = channel.whatsapp_partner_id
        #         emoji = messages['reaction'].get('emoji')
        #         whatsapp_message.mail_message_id._post_whatsapp_reaction(reaction_content=emoji, partner_id=partner_id)
        #         continue
        # else:
        #     _logger.warning("Unsupported whatsapp message type: %s", messages)
        #     continue
        # print ('==attachment==',attachment)
        # invoice.with_context(no_new_invoice=True).message_post(attachment_ids=[attachment.id])
        # attachment.write({'res_model': 'account.move', 'res_id': invoice.id})
        message = channel.message_post(message_type='whatsapp', **kwargs)
        # if attachment:
        #     message.write({'attachment_ids': [attachment.id]})
        #     attachment.write({'res_model': 'mail.channel', 'res_id': channel.id})
        # attachment.sudo().write({'res_id': channel.id})
        return channel